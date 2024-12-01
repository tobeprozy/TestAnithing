
#define USE_FFMPEG 1
#define USE_BMCV 1
#define USE_OPENCV 1

#include <cvwrapper.h>
#include <encoder.h>

#include "opencv2/opencv.hpp"
#include <stdio.h>
#include <iostream>
#include <string>

#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>


using namespace std;

// 线程安全的队列
template <typename T>
class SafeQueue {
private:
    std::queue<T> queue;
    mutable std::mutex mutex;
    std::condition_variable cond;
    size_t max_size;

public:
    explicit SafeQueue(size_t max_size) : max_size(max_size) {}

    // 禁用拷贝构造函数和拷贝赋值操作符
    SafeQueue(const SafeQueue&) = delete;
    SafeQueue& operator=(const SafeQueue&) = delete;

    // 移动构造函数
    SafeQueue(SafeQueue&& other) noexcept
        : max_size(std::exchange(other.max_size, 0)) {
        std::lock_guard<std::mutex> lock(other.mutex);
        queue = std::move(other.queue);
        // 注意：mutex 和 condition_variable 不能被移动，但它们的状态不需要被移动
    }

    // 移动赋值操作符
    SafeQueue& operator=(SafeQueue&& other) noexcept {
        if (this != &other) {
            std::unique_lock<std::mutex> lhs_lock(mutex, std::defer_lock);
            std::unique_lock<std::mutex> rhs_lock(other.mutex, std::defer_lock);
            std::lock(lhs_lock, rhs_lock);

            queue = std::move(other.queue);
            max_size = std::exchange(other.max_size, 0);
            // 注意：mutex 和 condition_variable 不能被移动，但它们的状态不需要被移动
        }
        return *this;
    }

    // // 入队操作
    // void enqueue(T value) {
    //     std::unique_lock<std::mutex> lock(mutex);
    //     cond.wait(lock, [this](){ return queue.size() < max_size; });
    //     queue.push(std::move(value));
    //     cond.notify_one();
    // }

    // // 出队操作
    // bool dequeue(T& value) {
    //     std::lock_guard<std::mutex> lock(mutex);
    //     if (queue.empty()) {
    //         return false;
    //     }
    //     value = std::move(queue.front());
    //     queue.pop();
    //     cond.notify_one();
    //     return true;
    // }

        // 入队操作，队列满时移除最早的元素
    void enqueue(T value) {
        std::unique_lock<std::mutex> lock(mutex);

        // 如果队列已满，移除最早的元素
        if (queue.size() == max_size) {
            queue.pop(); // 移除队列头部元素
        }
        
        queue.push(std::move(value)); // 添加新元素到队列尾部
        cond.notify_one(); // 通知正在等待的出队操作
    }

    // 出队操作，从队列中移除并获取最早的元素
    bool dequeue(T& value) {
        std::unique_lock<std::mutex> lock(mutex);
        cond.wait(lock, [this]() { return !queue.empty(); }); // 等待直到队列非空

        value = std::move(queue.front()); // 获取队列头部元素
        queue.pop(); // 移除队列头部元素

        // 如果队列未满，通知可能正在等待的入队操作
        if (queue.size() < max_size) {
            cond.notify_one();
        }

        return true;
    }

    // 检查队列是否为空
    bool empty() const {
        std::lock_guard<std::mutex> lock(mutex);
        return queue.empty();
    }

    // 获取队列的大小
    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex);
        return queue.size();
    }
};

void decode_and_enqueue(const std::string& video_path, SafeQueue<std::shared_ptr<sail::BMImage>>& queue, int device_id) {
    // 初始化解码器
    sail::Decoder decoder(video_path, true, device_id);
    auto handle = sail::Handle(device_id);
    // 解码过程
    while (true) {
        auto bmimg = std::make_shared<sail::BMImage>();
        int ret = decoder.read(handle,*bmimg);
        // std::cout << "read image from decoder,size: "<< queue.size() << std::endl;
        if (ret != 0) {
            // 解码失败或者视频流结束
            break;
        }
        queue.enqueue(bmimg);
        std::cout << "read image from decoder,size: "<< queue.size() << std::endl;
        
    }
}

void decode_and_enqueues(const std::string& video_path, SafeQueue<std::shared_ptr<sail::BMImage>>& queue, int device_id) {
    
    // 初始化解码器
    sail::Decoder decoder(video_path, true, device_id);
    auto handle = sail::Handle(device_id);
    int frame_interval=2; // 设置抽帧间隔，例如每5帧抽一帧
    int frame_counter = 0; // 用于抽帧的计数器
    // 解码过程
    while (true) {
        auto bmimg = std::make_shared<sail::BMImage>();
        int ret = decoder.read(handle, *bmimg);
        // std::vector<double> pts_dts = decoder.get_pts_dts();
        // std::cout << "pts: " << pts_dts[0] << endl;
        // std::cout << "dts: " << pts_dts[1] << endl;
        if (ret != 0) {
            break;
        }
        // 只有当 frame_counter 模 frame_interval 等于 0 时才处理当前帧
        if (frame_counter % frame_interval == 0) {
            queue.enqueue(bmimg);
            std::cout << "read image from decoder, size: " << queue.size() << std::endl;
        }
        frame_counter++; // 更新帧计数器
    }
}

void process_queue(SafeQueue<std::shared_ptr<sail::BMImage>>& queue, int queue_id,int device_id) {
    auto handle = sail::Handle(device_id);
    sail::Bmcv bmcv(handle);
    int count=0;
    std::vector<u_char> encoded_data;
    std::string ext = ".jpg";
    
    while (true) {
        std::shared_ptr<sail::BMImage> img;
        // 休眠 100 毫秒
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        if (queue.dequeue(img)) {
            // 处理图像
            std::cout << "Processing image from queue " << queue_id <<" size:"<<queue.size()<< std::endl;
            std::string filename = "output_" + std::to_string(queue_id) + "_" + std::to_string(count++) + ".jpg";
            // bmcv.imwrite(filename,*img);
            bool success = bmcv.imencode(ext, *img, encoded_data);
            for (size_t i = 1024*100; i < encoded_data.size() && i < 1024*100+10; ++i) {
                std::cout << static_cast<int>(encoded_data[i]) << " ";
            }
        }
    }
}

int main() {
    int device_id = 0;
    std::string video_url = "rtsp://admin:jdsm8888@27.151.43.4/Streaming/tracks/601?starttime=20240730T160518Z&endtime=20240730T161140Z"; // 视频URL
    int num_queues = 2;
    size_t max_queue_size = 10; // 队列的最大长度

    std::vector<SafeQueue<std::shared_ptr<sail::BMImage>>> queues;
    for (int i = 0; i < num_queues; ++i) {
        queues.emplace_back(max_queue_size);
    }


    std::vector<std::thread> threads;

    for (int i = 0; i < num_queues; ++i) {
        threads.emplace_back(decode_and_enqueues, video_url, std::ref(queues[i]), device_id);
        threads.emplace_back(process_queue, std::ref(queues[i]), i,device_id);
    }

    for (auto& thread : threads) {
        if (thread.joinable()) {
            thread.join();
        }
    }

    return 0;
}

