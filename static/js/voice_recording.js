$(document).ready(function() {
    let mediaRecorder;
    let audioChunks = [];
    let silenceTimer;
    const silenceThreshold = 2000; // 2 seconds of silence
    let silenceStart = null;
    let recordingStartTime;
    const minRecordingTime = 3000; // Minimum recording time of 3 seconds
    let stream;

    $("#startRecording").click(function() {
        audioChunks = []; // Clear audio chunks before starting a new recording
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(streamObj => {
                stream = streamObj;
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start(1000); // Record in 1-second chunks
                recordingStartTime = Date.now();

                $("#recordingStatus").text("Recording... (Will stop automatically after 2 seconds of silence)");

                mediaRecorder.addEventListener("dataavailable", function(event) {
                    audioChunks.push(event.data);
                });

                $("#startRecording").hide();
                $("#stopRecording").show();

                // Set up audio analysis for silence detection
                const audioContext = new AudioContext();
                const analyser = audioContext.createAnalyser();
                const microphone = audioContext.createMediaStreamSource(stream);
                microphone.connect(analyser);
                analyser.fftSize = 2048;
                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function checkSilence() {
                    analyser.getByteFrequencyData(dataArray);
                    const sum = dataArray.reduce((a, b) => a + b, 0);
                    const average = sum / bufferLength;
                    
                    if (average < 20) { // Increased threshold for better silence detection
                        if (silenceStart === null) {
                            silenceStart = Date.now();
                        } else if (Date.now() - silenceStart >= silenceThreshold && Date.now() - recordingStartTime >= minRecordingTime) {
                            stopRecording();
                        }
                    } else {
                        silenceStart = null;
                    }
                }

                // Start checking for silence
                silenceTimer = setInterval(checkSilence, 100);
            })
            .catch(error => {
                console.error("Error accessing microphone:", error);
                $("#recordingStatus").text("Error: Unable to access microphone. Please check your browser settings.");
                $("#recordingStatus").removeClass("text-success").addClass("text-danger");
            });
    });

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            clearInterval(silenceTimer);
            $("#startRecording").show();
            $("#stopRecording").hide();
            $("#recordingStatus").text("Processing...");

            mediaRecorder.addEventListener("stop", function() {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append("audio", audioBlob, "recording.wav");

                $.ajax({
                    url: "/add_voice_memory",
                    type: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function(response) {
                        if (response.success) {
                            $("#recordingStatus").text(response.message);
                            $("#recordingStatus").removeClass("text-danger").addClass("text-success");
                        } else {
                            $("#recordingStatus").text("Error: " + response.message);
                            $("#recordingStatus").removeClass("text-success").addClass("text-danger");
                        }
                        audioChunks = [];
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error("AJAX Error:", textStatus, errorThrown);
                        $("#recordingStatus").text("An error occurred while processing the voice memory. Please check the console for details.");
                        $("#recordingStatus").removeClass("text-success").addClass("text-danger");
                        audioChunks = [];
                    }
                });

                // Stop all tracks on the stream to release the microphone
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            });
        }
    }

    $("#stopRecording").click(stopRecording);
});
