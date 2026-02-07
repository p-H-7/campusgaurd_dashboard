"""
Download Phi-3-mini ONNX model optimized for Snapdragon X Elite NPU
"""

from huggingface_hub import snapshot_download
from pathlib import Path
import shutil

def download_phi3_onnx():
    print("="*60)
    print("Downloading Phi-3-mini ONNX for Snapdragon X Elite NPU")
    print("="*60)
    
    model_id = "microsoft/Phi-3-mini-4k-instruct-onnx"
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    print("\n📥 Downloading model (this may take 5-10 minutes)...")
    print(f"Model: {model_id}")
    
    # Download from HuggingFace
    cache_dir = snapshot_download(
        repo_id=model_id,
        allow_patterns=["cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/*"],
        cache_dir=str(models_dir / "cache"),
        local_dir=str(models_dir / "phi3"),
        local_dir_use_symlinks=False
    )
    
    print(f"\n✅ Model downloaded to: {models_dir / 'phi3'}")
    print(f"📊 Model size: ~2GB (quantized INT4)")
    
    # List downloaded files
    model_path = models_dir / "phi3" / "cpu_and_mobile" / "cpu-int4-rtn-block-32-acc-level-4"
    print(f"\n📁 Model files:")
    for f in model_path.glob("*"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")
    
    return model_path

if __name__ == "__main__":
    model_path = download_phi3_onnx()
    print(f"\n🚀 Ready to use! Model path: {model_path}")