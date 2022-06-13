.class public Lcom/fit2081/domainlogo/MainActivity;
.super Landroidx/appcompat/app/AppCompatActivity;
.source "MainActivity.java"


# instance fields
.field domainTv:Landroid/widget/EditText;

.field executor:Ljava/util/concurrent/ExecutorService;

.field handler:Landroid/os/Handler;

.field logoView:Landroid/widget/ImageView;


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 27
    invoke-direct {p0}, Landroidx/appcompat/app/AppCompatActivity;-><init>()V

    return-void
.end method


# virtual methods
.method public handleGetLogoBtn(Landroid/view/View;)V
    .locals 4
    .param p1, "v"    # Landroid/view/View;

    .line 57
    iget-object v0, p0, Lcom/fit2081/domainlogo/MainActivity;->domainTv:Landroid/widget/EditText;

    invoke-virtual {v0}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    .line 58
    .local v0, "theDomain":Ljava/lang/String;
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "https://logo.clearbit.com/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 64
    .local v1, "request":Ljava/lang/String;
    iget-object v2, p0, Lcom/fit2081/domainlogo/MainActivity;->executor:Ljava/util/concurrent/ExecutorService;

    new-instance v3, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda1;

    invoke-direct {v3, p0, v1}, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda1;-><init>(Lcom/fit2081/domainlogo/MainActivity;Ljava/lang/String;)V

    invoke-interface {v2, v3}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    .line 90
    return-void
.end method

.method public synthetic lambda$handleGetLogoBtn$0$com-fit2081-domainlogo-MainActivity(Landroid/graphics/Bitmap;)V
    .locals 1
    .param p1, "myBitmap"    # Landroid/graphics/Bitmap;

    .line 82
    iget-object v0, p0, Lcom/fit2081/domainlogo/MainActivity;->logoView:Landroid/widget/ImageView;

    invoke-virtual {v0, p1}, Landroid/widget/ImageView;->setImageBitmap(Landroid/graphics/Bitmap;)V

    .line 83
    return-void
.end method

.method public synthetic lambda$handleGetLogoBtn$1$com-fit2081-domainlogo-MainActivity(Ljava/lang/String;)V
    .locals 6
    .param p1, "request"    # Ljava/lang/String;

    .line 68
    :try_start_0
    new-instance v0, Ljava/net/URL;

    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V

    .line 69
    .local v0, "url":Ljava/net/URL;
    nop

    .line 70
    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;

    move-result-object v1

    check-cast v1, Ljava/net/HttpURLConnection;

    .line 71
    .local v1, "connection":Ljava/net/HttpURLConnection;
    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Ljava/net/HttpURLConnection;->setDoInput(Z)V

    .line 72
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->connect()V

    .line 75
    invoke-virtual {v1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object v2

    .line 78
    .local v2, "input":Ljava/io/InputStream;
    invoke-static {v2}, Landroid/graphics/BitmapFactory;->decodeStream(Ljava/io/InputStream;)Landroid/graphics/Bitmap;

    move-result-object v3

    .line 81
    .local v3, "myBitmap":Landroid/graphics/Bitmap;
    iget-object v4, p0, Lcom/fit2081/domainlogo/MainActivity;->handler:Landroid/os/Handler;

    new-instance v5, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;

    invoke-direct {v5, p0, v3}, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;-><init>(Lcom/fit2081/domainlogo/MainActivity;Landroid/graphics/Bitmap;)V

    invoke-virtual {v4, v5}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    .line 86
    nop

    .end local v0    # "url":Ljava/net/URL;
    .end local v1    # "connection":Ljava/net/HttpURLConnection;
    .end local v2    # "input":Ljava/io/InputStream;
    .end local v3    # "myBitmap":Landroid/graphics/Bitmap;
    goto :goto_0

    .line 84
    :catch_0
    move-exception v0

    .line 85
    .local v0, "e":Ljava/io/IOException;
    invoke-virtual {v0}, Ljava/io/IOException;->printStackTrace()V

    .line 89
    .end local v0    # "e":Ljava/io/IOException;
    :goto_0
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2
    .param p1, "savedInstanceState"    # Landroid/os/Bundle;

    .line 38
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    .line 39
    const v0, 0x7f0b001c

    invoke-virtual {p0, v0}, Lcom/fit2081/domainlogo/MainActivity;->setContentView(I)V

    .line 40
    const v0, 0x7f0800d6

    invoke-virtual {p0, v0}, Lcom/fit2081/domainlogo/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/ImageView;

    iput-object v0, p0, Lcom/fit2081/domainlogo/MainActivity;->logoView:Landroid/widget/ImageView;

    .line 41
    const v0, 0x7f08009e

    invoke-virtual {p0, v0}, Lcom/fit2081/domainlogo/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/EditText;

    iput-object v0, p0, Lcom/fit2081/domainlogo/MainActivity;->domainTv:Landroid/widget/EditText;

    .line 45
    invoke-static {}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor()Ljava/util/concurrent/ExecutorService;

    move-result-object v0

    iput-object v0, p0, Lcom/fit2081/domainlogo/MainActivity;->executor:Ljava/util/concurrent/ExecutorService;

    .line 51
    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    iput-object v0, p0, Lcom/fit2081/domainlogo/MainActivity;->handler:Landroid/os/Handler;

    .line 54
    return-void
.end method
