import time


#initialising the class
class TokenBucketLimiter:
    
    
    def __init__(self,capacity:int, refill_rate :float):
        
        self.capacity = capacity # initialise the capacity
        self.refill_rate = refill_rate #  the refill_rate in the given time
        self.buckets= {} # the basket of the requests
        
    def refill(self, client_id :str):
        now = time.time() 
        tokens , last_refill = self.buckets[client_id]     
        elapsed = now - last_refill
        new_tokens = elapsed * self.refill_rate          
        tokens = min(self.capacity , tokens+new_tokens)
        self.buckets[client_id] = [tokens,now]
        
    def allow_requests(self,client_id : str) -> bool:
        
        if client_id not in self.buckets:
            self.buckets[client_id] = [self.capacity , time.time()]
        self.refill(client_id)
        tokens , _ = self.buckets[client_id]
            
        if tokens >= 1:
            self.buckets[client_id][0] = tokens - 1
            return True
        return False
             
    def get_tokens(self , client_id : str) -> float:
        if client_id not in self.buckets:
            return self.capacity
        self.refill(client_id)
        return self.buckets[client_id][0]
             
            
        
        

