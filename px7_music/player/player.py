from px7_music.player.player_base import Player

class PlayerMPV(Player):
    def __init__(self):
        import mpv
        self.player = mpv.MPV(video=False, log_handler=None, loglevel="error")
        self._end_callback = None

        self.player.observe_property("eof-reached", self._on_end)

    def _on_end(self, name, value):
        if value and self._end_callback:
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
        return self.player.volume
    



class PlayerVLC(Player):
    def __init__(self):
        import vlc
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
        return self.player.audio_get_volume()


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