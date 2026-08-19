from px7_music.player import Player

class PlayerMPV(Player):
    def __init__(self):
        import mpv
        import os

        kwargs = {
            "video":         False, 
            "log_handler":   None, 
            "loglevel":      "error", 
            "audio_display": "no",
        }
        if "WSL_DISTRO_NAME" in os.environ or "WSL_INTEROP"  in os.environ: 
            kwargs["ao"] = "pulse"
            
        self._mpv   = mpv
        self.player = mpv.MPV(**kwargs)
        self._end_callback = None

        @self.player.event_callback(mpv.MpvEventID.END_FILE)
        def on_end(event):
            if event.data.reason == 0 and self._end_callback:
                self._end_callback()

        self._on_end_handler = on_end
    
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

    def set_volume(self, volume: int) -> int:
        volume = max(0, min(volume, 100))
        self.player.volume = volume
        return volume

    def get_volume(self) -> int:
        return int(self.player.volume)
    
    def get_state(self) -> str:
        if self.player.pause:
            return "Paused"
        if self.player.eof_reached:
            return "Ended"
        if self.player.core_idle:
            return "Idle"
        return "Playing"
    
    def get_time_pos(self) -> float | None:
        return self.player.time_pos
    
    def seek(self, seconds: int):
        try:
            self.player.seek(seconds, reference="absolute")
        except Exception as e:
            raise RuntimeError(f"Seek failed: {e}")
    
    def is_paused(self) -> bool:
        return bool(self.player.pause)
    
    def is_idle(self) -> bool:
        return bool(self.player.core_idle and not self.player.pause)


class PlayerVLC(Player):
    def __init__(self):
        import vlc
        self._vlc = vlc
        self.instance = vlc.Instance("--no-video --quiet")
        self.player = self.instance.media_player_new()
        self._end_callback = None
        self._volume = 100

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
        self.player.audio_set_volume(self._volume)

    def pause(self):
        self.player.pause()

    def resume(self):
        if not self.player.is_playing():
            self.player.play()

    def stop(self):
        self.player.stop()

    def set_volume(self, volume: int) -> int:
        volume = max(0, min(volume, 100))
        self._volume = volume
        self.player.audio_set_volume(volume)
        return volume
    
    def get_volume(self) -> int:
        vol = self.player.audio_get_volume()
        if vol == -1:
            return self._volume
        self._volume = int(vol)
        return self._volume
    
    def get_state(self) -> str:
        state = self.player.get_state()
        return {
            self._vlc.State.Playing:        "Playing",
            self._vlc.State.Paused:         "Paused",
            self._vlc.State.Ended:          "Ended",
            self._vlc.State.Stopped:        "Idle",
            self._vlc.State.NothingSpecial: "Idle",
        }.get(state, "Idle")
        
    def get_time_pos(self) -> float | None:
        pos = self.player.get_time()
        return pos / 1000 if pos > 0 else None
    
    def seek(self, seconds: int):
        length_ms = self.player.get_length()
        if length_ms <= 0:
            raise RuntimeError("Track length unavailable — seek not possible yet.")
        target_ms = max(0, min(seconds * 1000, length_ms))
        if self.player.set_time(target_ms) == -1:
            raise RuntimeError("VLC seek failed.")
    
    def is_paused(self) -> bool:
        return self.player.get_state() == self._vlc.State.Paused
    
    def is_idle(self):
        return self.player.get_state() in (
            self._vlc.State.NothingSpecial,
            self._vlc.State.Stopped,
            self._vlc.State.Ended,
        )


def get_player(forced_backend: str | None = None) -> tuple[str, Player] | tuple[None, None]:
    backends = (("mpv", PlayerMPV), ("vlc", PlayerVLC))

    if   forced_backend and forced_backend == "mpv":
        backends = (("mpv", PlayerMPV),)
    elif forced_backend and forced_backend == "vlc":
        backends = (("vlc", PlayerVLC),)

    for backend, cls in backends:
        try:
            return backend, cls()
        except Exception:
            continue
    return None, None