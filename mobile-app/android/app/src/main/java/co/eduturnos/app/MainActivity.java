package co.eduturnos.app;

import android.Manifest;
import android.content.ActivityNotFoundException;
import android.content.ContentUris;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.CalendarContract;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.getcapacitor.BridgeActivity;

import org.json.JSONObject;

import java.util.ArrayList;

public class MainActivity extends BridgeActivity {
    private static final int REQUEST_RECORD_AUDIO = 4002;
    private SpeechRecognizer voiceRecognizer;
    private boolean voiceStartPending;
    private boolean voiceCancellationRequested;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // EDUTURNOS loads its trusted HTTPS site in this Capacitor WebView.
        // A native bridge is required because Android browsers do not reliably
        // dispatch intent:// links originating from a remote page.
        getBridge().getWebView().addJavascriptInterface(new CalendarLauncher(), "EDUTURNOSNativeCalendar");
        getBridge().getWebView().addJavascriptInterface(new VoiceLauncher(), "EDUTURNOSNativeVoice");
    }

    @Override
    public void onDestroy() {
        voiceStartPending = false;
        voiceCancellationRequested = true;
        if (voiceRecognizer != null) voiceRecognizer.cancel();
        releaseVoiceRecognizer();
        super.onDestroy();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQUEST_RECORD_AUDIO) return;
        if (!voiceStartPending) return;
        voiceStartPending = false;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startVoiceRecognition();
        } else {
            dispatchVoiceEvent("eduturnos-native-voice-error", "error", "not-allowed");
        }
    }

    private void requestOrStartVoiceRecognition() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                == PackageManager.PERMISSION_GRANTED) {
            startVoiceRecognition();
            return;
        }
        voiceStartPending = true;
        ActivityCompat.requestPermissions(
                this,
                new String[]{Manifest.permission.RECORD_AUDIO},
                REQUEST_RECORD_AUDIO
        );
    }

    private void startVoiceRecognition() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            dispatchVoiceEvent("eduturnos-native-voice-error", "error", "unavailable");
            return;
        }
        releaseVoiceRecognizer();
        voiceCancellationRequested = false;
        voiceRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
        voiceRecognizer.setRecognitionListener(new RecognitionListener() {
            @Override
            public void onReadyForSpeech(Bundle params) {
                dispatchVoiceEvent("eduturnos-native-voice-ready", null, null);
            }

            @Override
            public void onBeginningOfSpeech() {
            }

            @Override
            public void onRmsChanged(float rmsdB) {
            }

            @Override
            public void onBufferReceived(byte[] buffer) {
            }

            @Override
            public void onEndOfSpeech() {
            }

            @Override
            public void onError(int error) {
                if (!voiceCancellationRequested) {
                    String message = error == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS
                            ? "not-allowed"
                            : error == SpeechRecognizer.ERROR_NO_MATCH
                                    || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT
                                    ? "no-speech"
                                    : "recognition";
                    dispatchVoiceEvent("eduturnos-native-voice-error", "error", message);
                    dispatchVoiceEvent("eduturnos-native-voice-end", null, null);
                }
                releaseVoiceRecognizer();
            }

            @Override
            public void onResults(Bundle results) {
                if (!voiceCancellationRequested) {
                    ArrayList<String> matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                    if (matches != null && !matches.isEmpty() && !matches.get(0).trim().isEmpty()) {
                        dispatchVoiceEvent("eduturnos-native-voice-result", "text", matches.get(0).trim());
                    } else {
                        dispatchVoiceEvent("eduturnos-native-voice-error", "error", "no-speech");
                    }
                    dispatchVoiceEvent("eduturnos-native-voice-end", null, null);
                }
                releaseVoiceRecognizer();
            }

            @Override
            public void onPartialResults(Bundle partialResults) {
            }

            @Override
            public void onEvent(int eventType, Bundle params) {
            }
        });

        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-CO")
                .putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
                .putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1);
        try {
            voiceRecognizer.startListening(intent);
        } catch (IllegalStateException | SecurityException error) {
            releaseVoiceRecognizer();
            dispatchVoiceEvent("eduturnos-native-voice-error", "error", "recognition");
        }
    }

    private void stopVoiceRecognition() {
        voiceStartPending = false;
        voiceCancellationRequested = true;
        if (voiceRecognizer != null) voiceRecognizer.cancel();
        releaseVoiceRecognizer();
        dispatchVoiceEvent("eduturnos-native-voice-end", null, null);
    }

    private void releaseVoiceRecognizer() {
        if (voiceRecognizer == null) return;
        SpeechRecognizer recognizer = voiceRecognizer;
        voiceRecognizer = null;
        recognizer.destroy();
    }

    private void dispatchVoiceEvent(String eventName, String key, String value) {
        String detail = key == null ? "{}" : "{"
                + JSONObject.quote(key) + ":" + JSONObject.quote(value) + "}";
        String script = "window.dispatchEvent(new CustomEvent("
                + JSONObject.quote(eventName)
                + ",{detail:"
                + detail
                + "}));";
        runOnUiThread(() -> getBridge().getWebView().evaluateJavascript(script, null));
    }

    private final class VoiceLauncher {
        @JavascriptInterface
        public void startListening() {
            runOnUiThread(MainActivity.this::requestOrStartVoiceRecognition);
        }

        @JavascriptInterface
        public void stopListening() {
            runOnUiThread(MainActivity.this::stopVoiceRecognition);
        }
    }

    private final class CalendarLauncher {
        @JavascriptInterface
        public void openAt(long startMillis) {
            runOnUiThread(() -> {
                Uri.Builder uri = CalendarContract.CONTENT_URI.buildUpon().appendPath("time");
                ContentUris.appendId(uri, startMillis > 0 ? startMillis : System.currentTimeMillis());
                Intent intent = new Intent(Intent.ACTION_VIEW)
                        .setData(uri.build())
                        .setPackage("com.google.android.calendar");
                try {
                    startActivity(intent);
                } catch (ActivityNotFoundException error) {
                    Toast.makeText(MainActivity.this,
                            "Google Calendar no está disponible en este dispositivo.", Toast.LENGTH_LONG).show();
                }
            });
        }

        @JavascriptInterface
        public void openEvent(String eventUrl) {
            runOnUiThread(() -> {
                Uri uri = Uri.parse(eventUrl == null ? "" : eventUrl);
                String eventId = uri.getQueryParameter("eid");
                if (!"https".equals(uri.getScheme())
                        || !"www.google.com".equals(uri.getHost())
                        || !"/calendar/event".equals(uri.getPath())
                        || eventId == null
                        || !eventId.matches("[A-Za-z0-9_-]+")) {
                    Toast.makeText(MainActivity.this,
                            "No se pudo validar la cita de Google Calendar.", Toast.LENGTH_LONG).show();
                    return;
                }

                Intent intent = new Intent(Intent.ACTION_VIEW, uri)
                        .setPackage("com.google.android.calendar");
                try {
                    startActivity(intent);
                } catch (ActivityNotFoundException error) {
                    Toast.makeText(MainActivity.this,
                            "Google Calendar no está disponible en este dispositivo.", Toast.LENGTH_LONG).show();
                }
            });
        }
    }
}
