.class Lcom/example/researchtestapp/SecondFragment$1;
.super Ljava/lang/Object;
.source "SecondFragment.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/example/researchtestapp/SecondFragment;->onViewCreated(Landroid/view/View;Landroid/os/Bundle;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/example/researchtestapp/SecondFragment;


# direct methods
.method constructor <init>(Lcom/example/researchtestapp/SecondFragment;)V
    .locals 0

    .line 32
    iput-object p1, p0, Lcom/example/researchtestapp/SecondFragment$1;->this$0:Lcom/example/researchtestapp/SecondFragment;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .locals 0

    .line 35
    iget-object p0, p0, Lcom/example/researchtestapp/SecondFragment$1;->this$0:Lcom/example/researchtestapp/SecondFragment;

    invoke-static {p0}, Landroidx/navigation/fragment/NavHostFragment;->findNavController(Landroidx/fragment/app/Fragment;)Landroidx/navigation/NavController;

    move-result-object p0

    const p1, 0x7f080033

    .line 36
    invoke-virtual {p0, p1}, Landroidx/navigation/NavController;->navigate(I)V

    return-void
.end method
