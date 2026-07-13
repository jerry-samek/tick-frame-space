import soundfile, numpy, scipy, matplotlib
print("soundfile:", soundfile.__version__)
print("numpy:", numpy.__version__)
print("scipy:", scipy.__version__)
print("matplotlib:", matplotlib.__version__)

# Test FLAC reading
sf_data, sr = soundfile.read(r"W:\workspace\tick-frame-space\experiments\trie_stream_filtering\v11\data\FLAC_11_secs_Small_75d2275409.flac")
print("\nFLAC sample loaded:")
print(f"  shape: {sf_data.shape}")
print(f"  sample_rate: {sr}")
print(f"  duration: {len(sf_data)/sr:.2f}s")
print(f"  dtype: {sf_data.dtype}")
print(f"  range: [{sf_data.min():.4f}, {sf_data.max():.4f}]")
