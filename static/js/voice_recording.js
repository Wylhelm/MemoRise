let mediaRecorder;
let audioChunks = [];
let stream;
const maxRecordingTime = 60000; // Maximum recording time of 60 seconds

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        $("#startRecording").show();
        $("#stopRecording").hide();
        $("#recordingStatus").text("Processing...");

        mediaRecorder.addEventListener("stop", function() {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = function() {
                const base64data = reader.result.split(',')[1];
                
                // First, send the audio data to initiate processing
                $.ajax({
                    url: "/add_voice_memory",
                    type: "POST",
                    data: JSON.stringify({ audio: base64data }),
                    contentType: "application/json",
                    success: function(response) {
                        console.log("Server response:", response);
                        if (response.status === 'processing') {
                            $("#recordingStatus").text("Processing audio data...");
                            // Start polling for processing status
                            pollProcessingStatus(base64data);
                        } else {
                            $("#recordingStatus").text("Error: " + response.message);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error("AJAX Error:", textStatus, errorThrown);
                        $("#recordingStatus").text("An error occurred while initiating voice memory processing.");
                    }
                });

                // Stop all tracks on the stream to release the microphone
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            };
        });
    }
}

function pollProcessingStatus(audioData) {
    let attempts = 0;
    const maxAttempts = 15; // Maximum number of polling attempts (30 seconds total)

    function poll() {
        $.ajax({
            url: "/process_voice_memory",
            type: "POST",
            data: JSON.stringify({ audio: audioData }),
            contentType: "application/json",
            success: function(response) {
                console.log("Processing status:", response);
                if (response.status === 'complete') {
                    $("#recordingStatus").text(response.message);
                } else if (response.status === 'error') {
                    $("#recordingStatus").text("Error: " + response.message);
                } else {
                    attempts++;
                    if (attempts < maxAttempts) {
                        $("#recordingStatus").text(response.message + " (Attempt " + attempts + "/" + maxAttempts + ")");
                        setTimeout(poll, 2000); // Poll every 2 seconds
                    } else {
                        $("#recordingStatus").text("Processing timed out. Please try again.");
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("AJAX Error:", textStatus, errorThrown);
                $("#recordingStatus").text("An error occurred while checking voice memory processing status.");
            }
        });
    }

    poll(); // Start polling
}

$(document).ready(function() {
    $("#startRecording").click(function() {
        audioChunks = []; // Clear audio chunks before starting a new recording
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(streamObj => {
                stream = streamObj;
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                $("#recordingStatus").text("Recording... (Max 60 seconds)");
                $("#startRecording").hide();
                $("#stopRecording").show();

                mediaRecorder.addEventListener("dataavailable", function(event) {
                    audioChunks.push(event.data);
                });

                // Automatically stop recording after maxRecordingTime
                setTimeout(stopRecording, maxRecordingTime);
            })
            .catch(error => {
                console.error("Error accessing microphone:", error);
                $("#recordingStatus").text("Error: Unable to access microphone. Please check your browser settings.");
            });
    });

    $("#stopRecording").click(stopRecording);
});
