import sophon.sail as sail
import argparse
import threading
import queue


def decode_and_enqueue(device_id: int, video_path: str, queues: list, queue_lock: threading.Lock, max_queue_size: int):
    handle = sail.Handle(device_id)
    bmcv = sail.Bmcv(handle)
    decoder = sail.Decoder(video_path, True, device_id)
    
    while True:
        image = decoder.read(handle)
        if image is None:
            break
        with queue_lock:
            idx = hash(image) % len(queues)
            try:
                queues[idx].put_nowait(image)
            except queue.Full:
                pass

def process_queue(queue, queue_id):
    while True:
        image = queue.get()
        print(f"推理xxx {queue_id}")

def main(device_id: int, video_path: str, num_queues: int, num_threads_per_queue: int, max_queue_size: int):
    queues = [queue.Queue(maxsize=max_queue_size) for _ in range(num_queues)]
    queue_lock = threading.Lock()

    decode_thread = threading.Thread(target=decode_and_enqueue, args=(device_id, video_path, queues, queue_lock, max_queue_size))
    decode_thread.start()

    for i in range(num_queues):
        thread = threading.Thread(target=process_queue, args=(queues[i], i))
        thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_id", type=int, default=0, help="dev_id")
    parser.add_argument("--video_path", type=str, required=True, help="Path to the video file")
    parser.add_argument("--num_queues", type=int, default=5, help="Number of queues")
    parser.add_argument("--num_threads_per_queue", type=int, default=5, help="Number of threads")
    parser.add_argument("--max_queue_size", type=int, default=10, help="Maximum size of each queue")
    args = parser.parse_args()

    main(args.device_id, args.video_path, args.num_queues, args.num_threads_per_queue, args.max_queue_size)