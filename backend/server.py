import grpc
from concurrent import futures
import time
import vda_pb2
import vda_pb2_grpc

class VideoService(vda_pb2_grpc.VideoServiceServicer):
    def Ping(self, request, context):
        return vda_pb2.Pong(message="Backend is Online!")

    def ProcessVideo(self, request, context):
        print(f"Received video: {request.file_path}")
        steps = ["Extracting Audio", "Running Whisper", "Analyzing Frames", "Done"]
        for i, step in enumerate(steps):
            time.sleep(1) # Simulate work
            yield vda_pb2.ProgressUpdate(status=step, percentage=(i+1)*25.0)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vda_pb2_grpc.add_VideoServiceServicer_to_server(VideoService(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()