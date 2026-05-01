class Player:
    def play(self, url: str):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError
    
    def resume(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def set_volume(self, volume: int):
        raise NotImplementedError
    
    def get_volume(self):
        raise NotImplementedError
    
    def _on_end(self, event):
        raise NotImplementedError
    
    def set_end_callback(self, callback):
        raise NotImplementedError