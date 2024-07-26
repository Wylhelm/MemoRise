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
                
                // Send the audio data for processing
                $.ajax({
                    url: "/add_voice_memory",
                    type: "POST",
                    data: JSON.stringify({ audio: base64data }),
                    contentType: "application/json",
                    success: function(response) {
                        console.log("Server response:", response);
                        if (response.status === 'complete') {
                            $("#recordingStatus").text(response.message);
                        } else {
                            $("#recordingStatus").text("Error: " + response.message);
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error("AJAX Error:", textStatus, errorThrown);
                        $("#recordingStatus").text("An error occurred while processing voice memory.");
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
