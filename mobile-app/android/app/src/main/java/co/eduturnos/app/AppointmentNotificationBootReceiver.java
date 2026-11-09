package co.eduturnos.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import org.json.JSONException;

public class AppointmentNotificationBootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) return;
        String action = intent.getAction();
        if (!Intent.ACTION_BOOT_COMPLETED.equals(action)
                && !Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)) {
            return;
        }
        try {
            AppointmentNotificationScheduler.restoreSchedule(context);
        } catch (JSONException | IllegalStateException | SecurityException error) {
            Log.e("EDUTURNOS", "Could not restore appointment reminders.", error);
        }
    }
}
