model_transform \
    --model_name bytetrack_s \
    --model_def ../bytetrack_s.onnx \
    --input_shapes [[1,3,608,1088]] \
    --keep_aspect_ratio \
    --pixel_format rgb \
    --test_input ./dog.jpg \
    --test_result bytetrack_s_top_outputs.npz \
    --mlir bytetrack_s.mlir

model_deploy \
    --mlir bytetrack_s.mlir \
    --quantize F32 \
    --processor bm1684 \
    --test_input bytetrack_s_in_f32.npz \
    --test_reference bytetrack_s_top_outputs.npz \
    --model bytetrack_s_v2_fp32.bmodel




model_transform.py \
    --model_name yolov10s \
    --model_def ..//yolov10s.onnx \
    --input_shapes [[1,3,640,640]] \
    --mean 0.0,0.0,0.0 \
    --scale 0.0039216,0.0039216,0.0039216 \
    --keep_aspect_ratio \
    --test_input ../bus.jpg \
    --test_result yolov10s_top_outputs.npz \
    --pixel_format rgb  \
    --tolerance 0.99,0.85 \
    --mlir yolov10s_1b.mlir 


run_calibration.py yolov10s_1b.mlir \
        --dataset ../datasets/coco128/ \
        --input_num 32 \
        -o yolov10s_cali_table


model_deploy.py \
        --mlir yolov10s_1b.mlir \
        --quantize INT8 \
        --chip bm1684x \
        --quantize_table ../models/onnx/qtable_y \
        --calibration_table yolov10s_cali_table \
        --model yolov10s_int8_1b_y.bmodel



model_deploy.py \
    --mlir swim_v10_20240703.mlir \
    --quantize F32 \
    --chip bm1684x \
    --test_input yolov10_in_f32.npz \
    --test_reference yolov10_outputs.npz \
    --model swim_v10_20240703_fp32_1b.bmodel

qtable_y
yolov10s_all_qtable
model_deploy.py \
        --mlir yolov10s_1b.mlir \
        --quantize INT8 \
        --chip bm1684x \
        --quantize_table ../models/onnx/qtable_y \
        --calibration_table yolov10s_cali_table \
        --test_input yolov10s_in_f32.npz \
        --test_reference yolov10s_top_outputs.npz \
        --model yolov10s_int8_1b_y.bmodel


fp_forward.py yolov10s_1b.mlir --fpfwd_outputs /model.19/cv2/act/Mul_output_0_Mul --fp_type F32  --processor bm1684x -o yolov10s_qtable1