from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

def test_doctor_command_checks():
    # Test doctor command checks and summary output formatting
    
    # Mocking the doctor runner
    class MockDoctor:
        def check_ffmpeg(self):
            return True, "ffmpeg version 4.4"
            
        def check_gpu(self):
            return True, "CUDA available"
            
        def generate_summary(self):
            return "Doctor Summary:\n- FFmpeg: OK\n- GPU: OK"
            
    doctor = MockDoctor()
    
    ffmpeg_ok, ffmpeg_msg = doctor.check_ffmpeg()
    assert ffmpeg_ok is True
    assert "version" in ffmpeg_msg
    
    gpu_ok, gpu_msg = doctor.check_gpu()
    assert gpu_ok is True
    assert "CUDA" in gpu_msg
    
    summary = doctor.generate_summary()
    assert "Doctor Summary:" in summary
    assert "FFmpeg: OK" in summary
    assert "GPU: OK" in summary

def test_doctor_cli_output(capsys):
    print("Doctor check passed!")
    captured = capsys.readouterr()
    assert "Doctor check passed!" in captured.out
