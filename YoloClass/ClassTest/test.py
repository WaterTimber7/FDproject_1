import cv2
import torch
from ultralytics import YOLO


def camera_realtime_detection(model_path, conf_threshold=0.5, camera_id=0):
    """
    摄像头实时检测程序

    参数:
    model_path: 训练好的模型权重路径
    conf_threshold: 置信度阈值
    camera_id: 摄像头设备ID (0=默认摄像头)
    """

    print(f"CUDA可用: {torch.cuda.is_available()}")
    print(f"加载模型: {model_path}")

    # 加载训练好的模型
    model = YOLO(model_path)

    # 打开摄像头
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"错误: 无法打开摄像头 {camera_id}")
        return

    # 获取摄像头分辨率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"摄像头分辨率: {width}x{height}, FPS: {fps}")
    print("按 'q' 键退出程序")
    print("按 's' 键保存当前帧")

    # 帧率计算变量
    frame_count = 0
    start_time = cv2.getTickCount()

    while True:
        # 读取帧
        ret, frame = cap.read()
        if not ret:
            print("错误: 无法读取摄像头画面")
            break

        frame_count += 1

        # 使用YOLO进行推理
        results = model(frame, conf=conf_threshold, verbose=False)[0]

        # 绘制检测结果
        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes

            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].cpu().numpy()
                cls_id = int(box.cls[0].cpu().numpy())

                # 获取类别名
                cls_name = model.names[cls_id] if cls_id < len(model.names) else f"Class {cls_id}"

                # 为不同类别选择颜色
                if cls_name == 'bending':
                    color = (0, 255, 0)  # 绿色 - 弯腰
                elif cls_name == 'down':
                    color = (0, 0, 255)  # 红色 - 跌倒
                elif cls_name == 'up':
                    color = (255, 0, 0)  # 蓝色 - 起身
                else:
                    color = (255, 255, 0)  # 青色 - 其他

                # 绘制边界框
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # 创建标签文本
                label = f"{cls_name} {conf:.2f}"

                # 计算标签文本大小
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )

                # 绘制标签背景
                cv2.rectangle(
                    frame,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width, y1),
                    color,
                    -1
                )

                # 绘制标签文本
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

        # 计算并显示帧率
        if frame_count % 30 == 0:
            current_time = cv2.getTickCount()
            elapsed_time = (current_time - start_time) / cv2.getTickFrequency()
            fps = frame_count / elapsed_time
            frame_count = 0
            start_time = current_time

        # 在画面左上角显示信息
        info_text = f"FPS: {fps:.1f} | Conf: {conf_threshold}"
        cv2.putText(frame, info_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 显示检测数量
        det_count = len(results.boxes) if results.boxes is not None else 0
        count_text = f"Detections: {det_count}"
        cv2.putText(frame, count_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 显示画面
        cv2.imshow('YOLOv11 跌倒检测 - 实时摄像头', frame)

        # 键盘输入处理
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):  # 按q退出
            print("退出程序")
            break
        elif key == ord('s'):  # 按s保存当前帧
            timestamp = cv2.getTickCount()
            filename = f"capture_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"已保存当前帧: {filename}")
        elif key == ord('+'):  # 按+增加置信度阈值
            conf_threshold = min(0.95, conf_threshold + 0.05)
            print(f"置信度阈值增加到: {conf_threshold:.2f}")
        elif key == ord('-'):  # 按-减少置信度阈值
            conf_threshold = max(0.1, conf_threshold - 0.05)
            print(f"置信度阈值减少到: {conf_threshold:.2f}")

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    print("摄像头已释放")


def main():
    # 设置你的模型路径
    # 注意：请根据你的实际情况修改这个路径
    MODEL_PATH = '../VideoProcess/best.pt'

    # 如果没有训练好的模型，可以使用官方预训练模型测试
    # MODEL_PATH = 'yolo11n.pt'

    # 摄像头实时检测
    camera_realtime_detection(
        model_path=MODEL_PATH,
        conf_threshold=0.5,  # 置信度阈值
        camera_id=0  # 摄像头ID，通常0是默认摄像头
    )


# 带命令行参数的版本
def run_with_args():
    import argparse

    parser = argparse.ArgumentParser(description='摄像头实时检测')
    parser.add_argument('--model', type=str, default='best.pt',
                        help='模型权重路径 (默认: best.pt)')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='置信度阈值 (默认: 0.5)')
    parser.add_argument('--camera', type=int, default=0,
                        help='摄像头ID (默认: 0)')

    args = parser.parse_args()

    camera_realtime_detection(
        model_path=args.model,
        conf_threshold=args.conf,
        camera_id=args.camera
    )


if __name__ == '__main__':
    # 直接运行主函数
    main()

    # 或者使用命令行参数
    # run_with_args()