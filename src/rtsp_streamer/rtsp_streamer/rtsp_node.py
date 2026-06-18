#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import threading
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

class RtspMultiStreamer(Node):
    def __init__(self):
        super().__init__('rtsp_multi_streamer')

        Gst.init(None)
        self.bridge = CvBridge()
        
        self.appsrc_pano = None
        self.appsrc_left = None
        self.appsrc_right = None

        self.ready_pano = False
        self.ready_left = False
        self.ready_right = False

        self.server = GstRtspServer.RTSPServer()
        self.server.props.service = "8554"
        self.mount = self.server.get_mount_points()

        self.sub_pano = self.create_subscription(Image, "camera/image_raw", self.callback_pano, 2)
        self.sub_left = self.create_subscription(Image, "camera/left/image_raw", self.callback_left, 2)
        self.sub_right = self.create_subscription(Image, "camera/right/image_raw", self.callback_right, 2)


    def create_pipeline_str(self, src_name, width, height):
        return (
            f"appsrc name={src_name} is-live=true block=true format=GST_FORMAT_TIME "
            f"caps=video/x-raw,format=BGR,width={width},height={height},framerate=30/1 "
            f"! queue max-size-buffers=1 max-size-time=0 max-size-bytes=0 leaky=downstream "
            f"! videoconvert ! video/x-raw,format=I420 "
            f"! x264enc speed-preset=ultrafast tune=zerolatency threads=2 bitrate=3000 "
            f"! rtph264pay config-interval=1 name=pay0 pt=96"
        )


    def setup_pano_factory(self, w, height):
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_shared(True)
        factory.set_launch(self.create_pipeline_str("src_pano", w, height))
        factory.connect("media-configure", lambda f, m: setattr(self, 'appsrc_pano', m.get_element().get_child_by_name("src_pano")))
        self.mount.add_factory("/stream", factory)
        self.get_logger().info(f"Доступен поток Панорамы: rtsp://192.168.65.87:8554/stream ({w}x{height})")
        self.ready_pano = True

    def setup_left_factory(self, w, height):
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_shared(True)
        factory.set_launch(self.create_pipeline_str("src_left", w, height))
        factory.connect("media-configure", lambda f, m: setattr(self, 'appsrc_left', m.get_element().get_child_by_name("src_left")))
        self.mount.add_factory("/stream_left", factory)
        self.get_logger().info(f"Доступен поток Левой камеры: rtsp://192.168.65.87:8554/stream_left ({w}x{height})")
        self.ready_left = True

    def setup_right_factory(self, w, height):
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_shared(True)
        factory.set_launch(self.create_pipeline_str("src_right", w, height))
        factory.connect("media-configure", lambda f, m: setattr(self, 'appsrc_right', m.get_element().get_child_by_name("src_right")))
        self.mount.add_factory("/stream_right", factory)
        self.get_logger().info(f"Доступен поток Правой камеры: rtsp://192.168.65.87:8554/stream_right ({w}x{height})")
        self.ready_right = True


    def push_to_gstreamer(self, msg, appsrc):
        if appsrc is None:
            return
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            data = frame.tobytes()
            buf = Gst.Buffer.new_allocate(None, len(data), None)
            buf.fill(0, data)
            
            timestamp = appsrc.get_current_running_time()
            buf.pts = timestamp
            buf.dts = timestamp
            
            appsrc.emit("push-buffer", buf)
        except Exception as e:
            self.get_logger().error(f"Ошибка отправки буфера: {str(e)}")

    def callback_pano(self, msg):
        if not self.ready_pano:
            self.setup_pano_factory(msg.width, msg.height)
            self.server.attach(None)
            return
        self.push_to_gstreamer(msg, self.appsrc_pano)

    def callback_left(self, msg):
        if not self.ready_left:
            self.setup_left_factory(msg.width, msg.height)
            self.server.attach(None)
            return
        self.push_to_gstreamer(msg, self.appsrc_left)

    def callback_right(self, msg):
        if not self.ready_right:
            self.setup_right_factory(msg.width, msg.height)
            self.server.attach(None)
            return
        self.push_to_gstreamer(msg, self.appsrc_right)


def main(args=None):
    rclpy.init(args=args)
    node = RtspMultiStreamer()

    gobject_loop = GObject.MainLoop()
    gobject_thread = threading.Thread(target=gobject_loop.run, daemon=True)
    gobject_thread.start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        gobject_loop.quit()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
