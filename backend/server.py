import grpc
from concurrent import futures
import vda_pb2
import vda_pb2_grpc
from core.orchestrator import VideoOrchestrator
import argparse
import os

class VideoService(vda_pb2_grpc.VideoServiceServicer):
    def __init__(self, db_path):

        if db_path is None:
            # Fallback that actually works on any Mac/Linux
            db_path = os.path.expanduser("~/Library/Application Support/com.intel.vda/vda_intelligence.db")
        
        print(f"--- 💾 Backend DB Path: {db_path} ---")
        self.orchestrator = VideoOrchestrator(db_path=db_path)

        self.db_dir = os.path.dirname(db_path)
        
    def Chat(self, request, context):
        print(f"Chat received for Video ID {request.video_id}: {request.message}")
        try:
            response_text = self.orchestrator.handle_chat(request.video_id, request.message)
            return vda_pb2.ChatResponse(reply=response_text)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return vda_pb2.ChatResponse()
        
    def Ping(self, request, context):
        return vda_pb2.Pong(message="AI Engine Online (arm64)")

    def ProcessVideo(self, request, context):
        print(f"Request to process: {request.file_path}")
        
        for status, progress in self.orchestrator.process_new_video(request.file_path):
            yield vda_pb2.ProgressUpdate(
                status=status,
                percentage=progress * 100
            )
        
        segments = [
            vda_pb2.VideoSegment(start_time=0.0, end_time=1.0, content=desc, segment_type="visual")
            for desc in self.orchestrator.current_descriptions
        ]
        
        final_payload = vda_pb2.AnalysisResult(
            transcription=self.orchestrator.current_transcript,
            summary="Video analysis complete.",
            segments=segments
        )

        yield vda_pb2.ProgressUpdate(
            status="Complete",
            percentage=100.0,
            final_data=final_payload
        )

def serve():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_path", type=str, required=True, help="Path to SQLite DB")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vda_pb2_grpc.add_VideoServiceServicer_to_server(VideoService(args.db_path), server)
    server.add_insecure_port('127.0.0.1:50051')
    print("🚀 gRPC Server running on 127.0.0.1:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()