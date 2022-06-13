# UI Analysis Examples

## v1.0

a single entry-point whole-program with multi-exits. The problem is to find invocation of certain external APIs.

```java
void main() { // entry point
    f();
} // exit 1

void f() {
    if (rand()) {
        externalAPI(); // target
    else {
        exit(); // exit 2
    }
}
```

Solution: build a Java call-graph using `main` as entry-point.

## v1.1

turn the whole program into an Service class which has lifecycle handlers (`onCreate`, `onFinish`) and event handler. onCreate handler or event handler might call lifecycle API `finish` to exit the service.

```java
class ExampleService extends Service {
    void onCreate() { ... }
    void onFinish() { ... }
    void onBackPressed(Event e) {
        ...
        this.finish();
    }
}
```

The platform code is similar to a event loop:

```java
class Service {
    boolean finished = false;
    void finish() {
    this.onFinish();
    finished = true;
    }
}

void main() {
    Service s = new Service();
    s.onCreate();
    for (Event e : waitEvent() if (!s.finished)) {
    if (e instanceof BackPressedEvent) {
        s.onBackPressed(e);
    }
    }
}
```

Solution: extra edges to turn iCFG to callback-iCFG. The context is still just simple java ones.

## v1.2

Introduce more Services that can call each other. One of them is MainService.

```java
class Service1 extends Service { ... }
class Service2 extends Service { ... }
class MainService extends Service {
    ...
    void onBackPressed(Event e) {
    startService(Service1.class);
    }
}
```

The `startService` API will “stack” the service calls and when the corresponding Service instance finished, the control flow will return back to the call-site. It is similar to call a function except that there are not args and `Service` has some built-in logic for lifecycles etc. Also, the event receiver context will change in that case as well.

Solution: model stack and use it as the context to determine event receiver, which in terms determine the callback-iCFG.

## v1.3

Introduce Dialog. Dialog is similar to a Service, except that it has a very simple and fixed UI structure that has a single button whose handler must be declared statically. Dialog is “showed” rather than created, but the meaning of API is similar. Also, Dialog has no lifecycle handlers. Its lifecycle finish API is called “dismiss”.

```java
class ExampleDialog extends Dialog {
    void onButtonClick() {
        ...
        this.dismiss();
    }
}

class MainService {
    void f() {
        ...
        showDialog(ExampleDialog.class);
    }
}
```

Extend window stack with Dialog as a frame.

## v1.4

Extend Dialog with dynamic allocation.

```java
class MainService {
    void f() {
        ...
        Dialog dialog = new ExampleDialog();
        dialog.show();
    }
}
```

This needs us analyze the type of local variables to resolve the virtual call. Backslicing in the application iCFG should be sufficient. Then propagate.


## v1.5

Extend Dialog with `DialogBuilder` and dynamic handler update.

```java
class MainService {
    void f() {
        ...
        Dialog dialog = DialogBuilder.create();
        dialog.setButtonOnClickListener(new OnClickListener() {
            void onClick(Context context) {
                ...
                context.finish();
            }
        });
        dialog.show();
    }
}
```

This requires tracking flow of anonymous `onClickListener` sub-class instance as part of control flow graph construction. Also, the `context` passed to the handler is the context Window, in this case, would be `dialog`. context can be `finsh`ed, and for `dialog`, that will be routed to its `dismiss`. But if `context` is an activity, the `finish` will be called.

Similarly, backslice and propagate. Needs passing “context” variable of `onClick` handler though, which should be sufficient if we know the window stack. (stack top will be the context).

## v1.6

Add static UI layout for Service. Each Service can select a static display. However, there will be no interaction on that display.

```java
class MainService {
    void onCreate() {
    this.setContentView(exampleLayoutId);
    ...
    }
}
```

exampleLayoutId can be statically resolved to a XML-defined layout tree and there will be separate logic for abstracting and reasoning about the layout tree. Each node in that layout tree is a view. The root is also called root view of the associated service.

Require XML parsing and some layout model.


## v1.7

View with interaction components with statically declared handlers.

For example, Button view inside the XML can have a declared `onClick = ExampleOnClickListener`. `ExampleOnClickListener` is defined in code as a sub-class of `OnClickListener`.

In this case, the event receiver context will be able to process more types of input, e.g. click, which will be routed to the handler of clicked element.  Also, that handler can start/show other service/dialog, or finish the `context`, in this case, would be the service associated with the root view of which layout tree the Button resides.

Require extending event receiver. This might impact callback-iCFG again.

## v1.8

Extend view with allocation and inflation.

```java
class MainService {
    void onCreate() {
    View v = new View();
    if (rand()) {
        v.inflate(exampleLayoutId);
    }
    this.setContentView(v);
    ...
    }
}
```

This requires tracking of the `inflate` call. Backslice & propagate.

## v1.9

Extend view with dynamic sub-view insertion and dynamic handler update.

```java
class MainService {
    void onCreate() {
    View v = new LinearLayout();
    if (rand()) {
        Button b = new Button();
        view.addView(b);
        b.setOnClickListener(...)
    }
    this.setContentView(v);
    ...
    }
}
```

This requires tracking of `addView` and `setOnClickListener` that updates the abstract view layout associated with local variables. Backslice & propagate.
