package co.eduturnos.app;

import android.app.Notification;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

public class AppointmentNotificationReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null
                || !AppointmentNotificationScheduler.ACTION_APPOINTMENT_NOTIFICATION.equals(
                        intent.getAction()
                )
                || !AppointmentNotificationScheduler.hasPermission(context)) {
            return;
        }

        int notificationId = intent.getIntExtra("notificationId", 0);
        int reminderMinutes = intent.getIntExtra("reminderMinutes", 0);
        if (notificationId == 0 || (reminderMinutes != 1440 && reminderMinutes != 120)) return;

        AppointmentNotificationScheduler.createChannel(
                context,
                AppointmentNotificationScheduler.CHANNEL_ID
        );
        String title = reminderMinutes == 1440 ? "Cita mañana" : "Cita en dos horas";
        String message = reminderMinutes == 1440
                ? "Tienes una cita mañana. Abre EDUTURNOS para ver los detalles."
                : "Tienes una cita en dos horas. Abre EDUTURNOS para ver los detalles.";
        Intent launchIntent = context.getPackageManager().getLaunchIntentForPackage(
                context.getPackageName()
        );
        if (launchIntent == null) launchIntent = new Intent(context, MainActivity.class);
        launchIntent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(
                context,
                notificationId,
                launchIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification notification = new NotificationCompat.Builder(
                context,
                AppointmentNotificationScheduler.CHANNEL_ID
        )
                .setSmallIcon(R.drawable.ic_notification)
                .setContentTitle(title)
                .setContentText(message)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(message))
                .setContentIntent(contentIntent)
                .setCategory(NotificationCompat.CATEGORY_EVENT)
                .setPriority(NotificationCompat.PRIORITY_DEFAULT)
                .setAutoCancel(true)
                .build();
        NotificationManagerCompat.from(context).notify(notificationId, notification);
    }
}
