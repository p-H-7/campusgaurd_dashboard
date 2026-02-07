"""
Local LLM running on Snapdragon X Elite NPU via ONNX Runtime
"""

import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np
from pathlib import Path
import json
from typing import Dict, List
import time

class NPU_LLM_Engine:
    def __init__(self):
        print("🚀 Initializing LLM on Snapdragon X Elite NPU...")
        
        # Model path
        self.model_path = Path("models/phi3/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4")
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please run download_llm.py first."
            )
        
        # Set up ONNX Runtime with DirectML (uses NPU)
        providers = [
            ('DmlExecutionProvider', {
                'device_id': 0,
            }),
            'CPUExecutionProvider'
        ]
        
        print(f"Available providers: {ort.get_available_providers()}")
        
        # Load tokenizer
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/Phi-3-mini-4k-instruct",
            trust_remote_code=True
        )
        
        # Load ONNX model
        print("Loading ONNX model...")
        model_file = self.model_path / "phi3-mini-4k-instruct-cpu-int4-rtn-block-32-acc-level-4.onnx"
        
        if not model_file.exists():
            # Try to find the model file
            onnx_files = list(self.model_path.glob("*.onnx"))
            if onnx_files:
                model_file = onnx_files[0]
                print(f"Using model: {model_file.name}")
            else:
                raise FileNotFoundError(f"No ONNX model found in {self.model_path}")
        
        self.session = ort.InferenceSession(
            str(model_file),
            providers=providers
        )
        
        # Check which provider is actually being used
        actual_provider = self.session.get_providers()[0]
        print(f"✅ Model loaded! Using: {actual_provider}")
        
        if actual_provider == 'DmlExecutionProvider':
            print("🎉 NPU acceleration active!")
        else:
            print("⚠️  Running on CPU (NPU not available)")
        
        self.initialized = True
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using the NPU-accelerated LLM
        """
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="np")
        input_ids = inputs["input_ids"].astype(np.int64)
        attention_mask = inputs["attention_mask"].astype(np.int64)
        
        # Prepare inputs for ONNX
        ort_inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
        
        # Run inference on NPU
        start_time = time.time()
        outputs = self.session.run(None, ort_inputs)
        inference_time = time.time() - start_time
        
        # Decode output
        output_ids = outputs[0]
        response = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        print(f"⚡ NPU inference time: {inference_time:.2f}s")
        
        return response
    
    def analyze_alerts(self, alert_text: str, yes_count: int, maybe_count: int, total: int, lookback_minutes: int) -> Dict:
        """
        Analyze security alerts using NPU-accelerated LLM
        """
        
        prompt = f"""<|system|>
You are a campus security AI assistant analyzing real-time safety alerts. Provide threat assessment in strict JSON format.
<|end|>
<|user|>
Analyze these campus security alerts from the last {lookback_minutes} minutes:

{alert_text}

STATISTICS:
- Total alerts: {total}
- Confirmed threats (YES): {yes_count}
- Uncertain (MAYBE): {maybe_count}

Provide your assessment as a JSON object with these exact fields:
{{
  "threat_level": "CRITICAL" or "HIGH" or "MEDIUM" or "LOW",
  "summary": "2-3 sentence assessment",
  "recommendations": ["action 1", "action 2", "action 3"],
  "alert_security": true or false
}}

Respond ONLY with the JSON object, no other text.
<|end|>
<|assistant|>
"""

        print(f"\n🧠 Analyzing {total} alerts on NPU...")
        
        try:
            # Generate response using NPU
            response = self.generate_text(prompt, max_tokens=300)
            
            # Extract JSON from response
            response = response.strip()
            
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                print("⚠️  No JSON found in response, using fallback")
                return self._fallback_analysis(yes_count, maybe_count, total)
            
            json_str = response[start:end]
            result = json.loads(json_str)
            
            # Validate required fields
            required = ["threat_level", "summary", "recommendations", "alert_security"]
            if not all(k in result for k in required):
                print("⚠️  Invalid JSON structure, using fallback")
                return self._fallback_analysis(yes_count, maybe_count, total)
            
            print("✅ NPU analysis complete")
            result["npu_processed"] = True
            return result
            
        except Exception as e:
            print(f"❌ NPU analysis error: {e}")
            print("Using fallback analysis...")
            return self._fallback_analysis(yes_count, maybe_count, total)
    
    def _fallback_analysis(self, yes_count: int, maybe_count: int, total: int) -> Dict:
        """
        Fallback rule-based analysis if LLM fails
        """
        if yes_count >= 3:
            return {
                "threat_level": "CRITICAL",
                "summary": f"🚨 {yes_count} confirmed threats detected. Immediate response required.",
                "recommendations": [
                    "🚨 Dispatch security immediately",
                    "📞 Contact campus police",
                    "📹 Review all camera feeds",
                    "🔒 Prepare lockdown procedures"
                ],
                "alert_security": True,
                "npu_processed": False
            }
        elif yes_count >= 1:
            return {
                "threat_level": "HIGH",
                "summary": f"⚠️ {yes_count} confirmed, {maybe_count} uncertain incidents.",
                "recommendations": [
                    "👮 Increase security patrols",
                    "📱 Notify supervisor",
                    "🔍 Investigate incidents"
                ],
                "alert_security": True,
                "npu_processed": False
            }
        elif maybe_count >= 1:
            return {
                "threat_level": "MEDIUM",
                "summary": f"Moderate activity: {maybe_count} alerts need verification.",
                "recommendations": [
                    "🔍 Verify uncertain alerts",
                    "👁️ Maintain awareness",
                    "📋 Document incidents"
                ],
                "alert_security": False,
                "npu_processed": False
            }
        else:
            return {
                "threat_level": "LOW",
                "summary": "✅ Normal operations. No threats.",
                "recommendations": ["✓ Continue monitoring"],
                "alert_security": False,
                "npu_processed": False
            }

# Singleton instance
_npu_engine = None

def get_npu_engine():
    """Get or create NPU LLM engine"""
    global _npu_engine
    if _npu_engine is None:
        _npu_engine = NPU_LLM_Engine()
    return _npu_engine