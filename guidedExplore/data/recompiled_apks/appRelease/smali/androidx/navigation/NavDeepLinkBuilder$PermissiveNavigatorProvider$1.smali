.class Landroidx/navigation/NavDeepLinkBuilder$PermissiveNavigatorProvider$1;
.super Landroidx/navigation/Navigator;
.source "NavDeepLinkBuilder.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Landroidx/navigation/NavDeepLinkBuilder$PermissiveNavigatorProvider;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Landroidx/navigation/Navigator<",
        "Landroidx/navigation/NavDestination;",
        ">;"
    }
.end annotation


# instance fields
.field final synthetic this$0:Landroidx/navigation/NavDeepLinkBuilder$PermissiveNavigatorProvider;


# direct methods
.method constructor <init>(Landroidx/navigation/NavDeepLinkBuilder$PermissiveNavigatorProvider;)V
    .locals 0

    .line 273
    iput-object p1, p0, Landroidx/navigation/NavDeepLinkBuilder$PermissiveNavigatorProvider$1;->this$0:Landroidx/navigation/NavDeepLinkBuilder$PermissiveNavigatorProvider;

    invoke-direct {p0}, Landroidx/navigation/Navigator;-><init>()V

    return-void
.end method


# virtual methods
.method public createDestination()Landroidx/navigation/NavDestination;
    .locals 1

    .line 277
    new-instance p0, Landroidx/navigation/NavDestination;

    const-string v0, "permissive"

    invoke-direct {p0, v0}, Landroidx/navigation/NavDestination;-><init>(Ljava/lang/String;)V

    return-object p0
.end method

.method public navigate(Landroidx/navigation/NavDestination;Landroid/os/Bundle;Landroidx/navigation/NavOptions;Landroidx/navigation/Navigator$Extras;)Landroidx/navigation/NavDestination;
    .locals 0

    .line 285
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "navigate is not supported"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public popBackStack()Z
    .locals 1

    .line 290
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string v0, "popBackStack is not supported"

    invoke-direct {p0, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method
