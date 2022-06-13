package com.example.my_first_app;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;



public class MainActivity extends AppCompatActivity {
    public static final String EXTRA_MESSAGE = "com.example.myfirstapp.MESSAGE";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }


    public void sendMessage(View view) {
        Intent intent = new Intent(this, DisplayMessageActivity.class);
        EditText editText = (EditText) findViewById(R.id.editText);
        String message = editText.getText().toString();
        intent.putExtra(EXTRA_MESSAGE, message);
        startActivity(intent);
    }


    public void fire(View view) {
        FireMissilesDialogFragment diag = new FireMissilesDialogFragment();
        diag.show(getSupportFragmentManager(), "missiles");
    }

    public void fire2(View view) {
        FireMissilesDialogFragment2 diag2 = new FireMissilesDialogFragment2();
        diag2.show(getSupportFragmentManager(), "missiles2");
    }
}