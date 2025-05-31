import redis
import json

if __name__=="__main__":

    subscribers_arrays = ["meopw","msdfasdfasfd"]
    r = redis.Redis(host='localhost', port=6379,db=1)

    # Store the list in Redis as a JSON string
    r.set("entries", json.dumps(subscribers_arrays))

    # Optional: To retrieve and decode later
    cached_entries = json.loads(r.get("entries"))
    print(cached_entries)  # ['1@gmail.com', '2@gmail.com']