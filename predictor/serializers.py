from rest_framework import serializers

class PredictSerializer(serializers.Serializer):
    audio_file = serializers.FileField(required=False)
    image_file = serializers.ImageField(required=False)
    use_audio = serializers.BooleanField(default=True)
    use_image = serializers.BooleanField(default=False)
    combine_features = serializers.BooleanField(default=True)
    return_spectrogram = serializers.BooleanField(default=False)
    return_heatmap = serializers.BooleanField(default=False)
    generate_report = serializers.BooleanField(default=False)

    # ✅ Add user info fields
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
