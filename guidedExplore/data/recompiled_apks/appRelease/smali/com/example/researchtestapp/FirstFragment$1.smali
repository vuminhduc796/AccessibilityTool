.class Lcom/example/researchtestapp/FirstFragment$1;
.super Ljava/lang/Object;
.source "FirstFragment.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/example/researchtestapp/FirstFragment;->onViewCreated(Landroid/view/View;Landroid/os/Bundle;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/example/researchtestapp/FirstFragment;


# direct methods
.method constructor <init>(Lcom/example/researchtestapp/FirstFragment;)V
    .locals 0

    .line 32
    iput-object p1, p0, Lcom/example/researchtestapp/FirstFragment$1;->this$0:Lcom/example/researchtestapp/FirstFragment;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 0

    .line 35
    iget-object p0, p0, Lcom/example/researchtestapp/FirstFragment$1;->this$0:Lcom/example/researchtestapp/FirstFragment;

    invoke-static {p0}, Landroidx/navigation/fragment/NavHostFragment;->findNavController(Landroidx/fragment/app/Fragment;)Landroidx/navigation/NavController;

    move-result-object p0

    const p1, 0x7f080032

    .line 36
    invoke-virtual {p0, p1}, Landroidx/navigation/NavController;->navigate(I)V

    return-void
.end method
