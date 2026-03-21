import grpc
from concurrent import futures
import vda_pb2
import vda_pb2_grpc
from core.orchestrator import VideoOrchestrator

class VideoService(vda_pb2_grpc.VideoServiceServicer):
    def __init__(self):
        # Initialize orchestrator once when server starts
        self.orchestrator = VideoOrchestrator()

    def Ping(self, request, context):
        return vda_pb2.Pong(message="AI Engine Online (arm64)")

    def ProcessVideo(self, request, context):
        print(f"Request to process: {request.file_path}")
        
        # Call orchestrator and stream progress back to Tauri
        for status, progress in self.orchestrator.process_new_video(request.file_path):
            yield vda_pb2.ProgressUpdate(
                status=status,
                percentage=progress * 100
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vda_pb2_grpc.add_VideoServiceServicer_to_server(VideoService(), server)
    server.add_insecure_port('127.0.0.1:50051')
    print("🚀 gRPC Server running on 127.0.0.1:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()