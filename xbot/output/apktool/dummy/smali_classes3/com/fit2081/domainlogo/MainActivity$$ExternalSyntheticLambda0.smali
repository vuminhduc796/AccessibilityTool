.class public final synthetic Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Ljava/lang/Runnable;


# instance fields
.field public final synthetic f$0:Lcom/fit2081/domainlogo/MainActivity;

.field public final synthetic f$1:Landroid/graphics/Bitmap;


# direct methods
.method public synthetic constructor <init>(Lcom/fit2081/domainlogo/MainActivity;Landroid/graphics/Bitmap;)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;->f$0:Lcom/fit2081/domainlogo/MainActivity;

    iput-object p2, p0, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;->f$1:Landroid/graphics/Bitmap;

    return-void
.end method


# virtual methods
.method public final run()V
    .locals 2

    iget-object v0, p0, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;->f$0:Lcom/fit2081/domainlogo/MainActivity;

    iget-object v1, p0, Lcom/fit2081/domainlogo/MainActivity$$ExternalSyntheticLambda0;->f$1:Landroid/graphics/Bitmap;

    invoke-virtual {v0, v1}, Lcom/fit2081/domainlogo/MainActivity;->lambda$handleGetLogoBtn$0$com-fit2081-domainlogo-MainActivity(Landroid/graphics/Bitmap;)V

    return-void
.end method
