from px7_music.player.player_base import Player

class PlayerMPV(Player):
    def __init__(self):
        import mpv
        self._mpv = mpv
        self.player = mpv.MPV(video=False, log_handler=None, loglevel="error")
        self._end_callback = None

        @self.player.event_callback(mpv.MpvEventID.END_FILE)
        def on_end(event):
            if event.data.reason == 0:
                if self._end_callback:
                    self._end_callback()

        self._on_end_handler = on_end

    def _on_end(self, event):
        if event.event_id == self._mpv.MPV_EVENT_END_FILE:
            if self._end_callback:
                self._end_callback()
    
    def set_end_callback(self, callback):
        self._end_callback = callback

    def play(self, url: str):
        self.player.play(url)

    def pause(self):
        self.player.pause = True
    
    def resume(self):
        self.player.pause = False

    def stop(self):
        self.player.stop()

    def set_volume(self, volume: int):
        volume = max(0, min(volume, 100))
        self.player.volume = volume
        return volume

    def get_volume(self):
        return int(self.player.volume)
    
    def get_state(self):
        if self.player.pause:
            return "Paused"
        
        if self.player.eof_reached:
            return "Ended"
        
        if self.player.core_idle:
            return "Idle"

        return "Playing"
    
    def get_time_pos(self):
        return self.player.time_pos
    
    def seek(self, seconds: int):
        try:
            self.player.seek(seconds, reference="absolute")
        except Exception as e:
            raise RuntimeError(f"Seek failed: {e}")
    
    def is_paused(self):
        return self.player.pause
    
    def is_idle(self):
        return self.player.core_idle and not self.player.pause



class PlayerVLC(Player):
    def __init__(self):
        import vlc
        self._vlc = vlc
        self.instance = vlc.Instance("--no-video --quiet")
        self.player = self.instance.media_player_new()
        self._end_callback = None

        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end)

    def _on_end(self, event):
        if self._end_callback:
            self._end_callback()

    def set_end_callback(self, callback):
        self._end_callback = callback

    def play(self, url: str):
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.play()

    def pause(self):
        self.player.pause()

    def resume(self):
        if not self.player.is_playing():
            self.player.play()

    def stop(self):
        self.player.stop()

    def set_volume(self, volume: int):
        volume = max(0, min(volume, 100))
        result = self.player.audio_set_volume(volume)
        if result == -1:
            raise RuntimeError("VLC failed to set volume")
        return volume
    
    def get_volume(self):
        return int(self.player.audio_get_volume())
    
    def get_state(self):
        state = self.player.get_state()

        if state == self._vlc.State.Playing:
            return "Playing"
        elif state == self._vlc.State.Paused:
            return "Paused"
        elif state == self._vlc.State.Ended:
            return "Ended"
        elif state == self._vlc.State.Stopped:
            return "Idle"
        elif state == self._vlc.State.NothingSpecial:
            return "Idle"
        else:
            return "Idle"
        
    def get_time_pos(self):
        pos = self.player.get_time()
        if pos <= 0:
            return 0
        return pos / 1000
    
    def seek(self, seconds: int):
        length_ms = self.player.get_length()
        if length_ms <= 0:
            raise RuntimeError("Track length unavailable — seek not possible yet.")
        target_ms = max(0, min(seconds * 1000, length_ms))
        if self.player.set_time(target_ms) == -1:
            raise RuntimeError("VLC seek failed.")
    
    def is_paused(self):
        return self.player.get_state() == self._vlc.State.Paused
    
    def is_idle(self):
        state = self.player.get_state()
        return state in (
            self._vlc.State.NothingSpecial,
            self._vlc.State.Stopped,
            self._vlc.State.Ended
        )


def get_player():
    # --- MPV ---
    try:
        return "mpv", PlayerMPV()
    except Exception:
        pass

    # --- VLC ---
    try:
        return "vlc", PlayerVLC()
    except Exception:
        pass

    return None, None