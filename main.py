#!/usr/bin/env python

import sys
import gi
from multiprocessing import Process
import os

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

Gst.init(None)

class TestRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, file_location):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.file_location = file_location

    def do_create_element(self, url):
        # Set mp4 file path to filesrc's location property
        src_demux = f"filesrc location={self.file_location} ! qtdemux name=demux"
        h264_transcode = "demux.video_0"
        # Uncomment the following line if video transcoding is necessary
        # h264_transcode = "demux.video_0 ! decodebin ! queue ! x264enc"
        pipeline = "{0} {1} ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(src_demux, h264_transcode)
        print("Element created: " + pipeline)
        return Gst.parse_launch(pipeline)

class GstreamerRtspServer():
    def __init__(self, stream_name, file_location, port):
        self.rtspServer = GstRtspServer.RTSPServer()
        self.rtspServer.set_service(str(port))  # Set the port for the RTSP server
        self.stream_name = stream_name
        factory = TestRtspMediaFactory(file_location)
        factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory(f"/{stream_name}", factory)
        self.rtspServer.attach(None)

    def run(self):
        loop = GLib.MainLoop()
        print(f"Starting stream at rtsp://localhost:{self.rtspServer.get_service()}/{self.stream_name}")
        loop.run()

def start_rtsp_stream(stream_name, file_location, port):
    # Start a new RTSP server for each stream in a separate process
    server = GstreamerRtspServer(stream_name, file_location, port)
    server.run()

if __name__ == '__main__':
    # Define different RTSP streams and their corresponding files
    streams = [
        {"name": "stream1", "file": "/home/kartikeya/Office/RTSP_Server/crowd_test.mp4", "port": 8551},
        {"name": "stream2", "file": "/home/kartikeya/Office/RTSP_Server/crowd_test.mp4", "port": 8552},
        {"name": "stream3", "file": "/home/kartikeya/Office/RTSP_Server/crowd_test.mp4", "port": 8553},
        {"name": "stream4", "file": "/home/kartikeya/Office/RTSP_Server/crowd_test.mp4", "port": 8554},
        # {"name": "stream5", "file": "/home/kartikeya/Office/RTSP_Server/crowd_test.mp4", "port": 8555},
        # {"name": "stream6", "file": "/home/kartikeya/Office/RTSP_Server/crowd_test.mp4", "port": 8556},
    ]

    # Create a process for each stream with a different port
    processes = []
    for stream in streams:
        p = Process(target=start_rtsp_stream, args=(stream['name'], stream['file'], stream['port']))
        p.daemon = True
        p.start()
        processes.append(p)

    # Wait for all processes to complete
    for p in processes:
        p.join()
