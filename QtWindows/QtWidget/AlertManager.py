import os
import threading
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from logger import app_logger

class AudioAlertManager:
    """
    单例音频报警管理器
    所有YOLO检测类共享同一个实例，只播放一次音频
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化音频播放器"""
        if self._initialized:
            return
            
        self.sound_player = QMediaPlayer()
        self.sound_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "UI", "worn_video.mp3")
        self.is_playing = False
        self._initialized = True
        
        # 连接媒体状态变化信号
        self.sound_player.mediaStatusChanged.connect(self._handle_media_status)
        
        print("音频报警管理器初始化完成")
    
    def play_alert_sound(self):
        """
        播放警报音频
        如果正在播放则不操作，否则播放一次worn_video.mp3
        """
        if self.is_playing:
            # 静默跳过，不输出日志
            return False
        
        if not os.path.exists(self.sound_file):
            print(f"音频文件不存在: {self.sound_file}")
            return False

        try:
            media_content = QMediaContent(QUrl.fromLocalFile(self.sound_file))
            self.sound_player.setMedia(media_content)
            self.sound_player.setVolume(80)
            self.sound_player.play()
            self.is_playing = True
            print("开始播放警报音频")
            return True
        except Exception as e:
            print(f"播放警报音频失败: {str(e)}")
            return False
    
    def _handle_media_status(self, status):
        """处理媒体状态变化"""
        if status == QMediaPlayer.EndOfMedia:
            # 音频播放结束，静默重置状态
            self.is_playing = False
        # 移除其他状态变化的调试信息
    
    def stop_alert_sound(self):
        """停止播放警报音频"""
        if self.is_playing:
            self.sound_player.stop()
            self.is_playing = False
            print("停止播放警报音频")
    
    def is_sound_playing(self):
        """检查音频是否正在播放"""
        return self.is_playing

class AlertManager(QObject):
    """警报管理器，处理多个警报和声音播放"""
    
    alert_triggered = pyqtSignal(str, str)  # 信号：摄像头名称，警报信息
    
    def __init__(self):
        super().__init__()
        self.active_alerts = {}  # 活跃的警报 {alert_id: QMessageBox}
        self.sound_player = QMediaPlayer()
        self.sound_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "UI", "worn_video.mp3")
        self.is_playing_sound = False
        self.alert_counter = 0
        
        # 连接信号
        self.alert_triggered.connect(self._show_alert_dialog)
        
        print("警报管理器初始化完成")
    
    def trigger_alert(self, camera_name, detection_info):
        """触发警报"""
        alert_id = f"{camera_name}_{self.alert_counter}"
        self.alert_counter += 1
        
        # 发送信号（确保在主线程中显示对话框）
        self.alert_triggered.emit(alert_id, f"{camera_name}检测到目标\n\n检测信息：{detection_info}")
        
        # 开始播放声音（如果还没有播放）
        self._start_sound_playback()
        
        print(f"触发警报：{camera_name} - {detection_info}")
    
    def _show_alert_dialog(self, alert_id, message):
        """显示警报对话框（在主线程中执行）"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("检测警报")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # 设置对话框关闭时的回调
        msg_box.finished.connect(lambda result, aid=alert_id: self._alert_closed(aid))
        
        # 记录活跃警报
        self.active_alerts[alert_id] = msg_box
        
        # 显示对话框（非模态，允许多个同时显示）
        msg_box.show()
    
    def _alert_closed(self, alert_id):
        """警报对话框被关闭时的处理"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            print(f"警报 {alert_id} 已被确认")
        
        # 如果没有活跃警报，停止声音
        if not self.active_alerts and self.is_playing_sound:
            self._stop_sound_playback()
    
    def _start_sound_playback(self):
        """开始播放提示声音"""
        if not self.is_playing_sound and os.path.exists(self.sound_file):
            try:
                media_content = QMediaContent(QUrl.fromLocalFile(self.sound_file))
                self.sound_player.setMedia(media_content)
                self.sound_player.setVolume(80)
                self.sound_player.play()
                self.is_playing_sound = True
                print("开始播放警报声音")
                
                # 设置循环播放
                self.sound_player.mediaStatusChanged.connect(self._handle_media_status)
            except Exception as e:
                print(f"播放警报声音失败: {str(e)}")
    
    def _handle_media_status(self, status):
        """处理媒体状态变化，实现循环播放"""
        if status == QMediaPlayer.EndOfMedia and self.is_playing_sound:
            # 循环播放
            self.sound_player.setPosition(0)
            self.sound_player.play()
    
    def _stop_sound_playback(self):
        """停止播放提示声音"""
        if self.is_playing_sound:
            self.sound_player.stop()
            self.is_playing_sound = False
            print("停止播放警报声音")
    
    def close_all_alerts(self):
        """关闭所有活跃警报"""
        for alert_id, msg_box in list(self.active_alerts.items()):
            msg_box.close()
        self.active_alerts.clear()
        self._stop_sound_playback()