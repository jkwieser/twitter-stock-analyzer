from abc import ABC, abstractmethod
import datetime


class Requestor(ABC):
    
    
    @abstractmethod
    def request_new(self) -> [{}]:
        pass
    
    
    def get_time(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")