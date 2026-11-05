package co.eduturnos.app;

import android.content.ActivityNotFoundException;
import android.content.ContentUris;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.CalendarContract;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // EDUTURNOS loads its trusted HTTPS site in this Capacitor WebView.
        // A native bridge is required because Android browsers do not reliably
        // dispatch intent:// links originating from a remote page.
        getBridge().getWebView().addJavascriptInterface(new CalendarLauncher(), "EDUTURNOSNativeCalendar");
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
    }
}
