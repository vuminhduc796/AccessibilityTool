package com.example.test01;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

import java.util.Random;

/**
 * For testing purpose
 *
 * FIXME: extend to framework harness to support testing on Java/Class file directly
 */
public class Main3Activity extends AppCompatActivity {
    static class Obj {
        int field = 0;
    }

    static void updateObj(Obj o) {
        o.field = 1;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // state: {}
        Obj obj = new Obj();
        // state: { obj.field -> 0 }
        updateObj(obj);
        // state: { obj.field -> 1 }

        Random rand = new Random();
        if (rand.nextInt() % 2 == 1) {
            obj.field = 3;
        }
        // state: { obj.field -> {1, 3} }
        if (obj.field == 1) {
            // state: { obj.field -> 1 }
            obj.field += 2;
            // state: { obj.field -> 3 }
        } else {
            // state: { obj.field -> 3 }
            obj.field += 3;
            // state: { obj.field -> 6 }
        }
        // state: { obj.field -> {3, 6} }
    }
}
