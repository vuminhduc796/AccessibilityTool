.class Landroidx/navigation/NavType$7;
.super Landroidx/navigation/NavType;
.source "NavType.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Landroidx/navigation/NavType;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Landroidx/navigation/NavType<",
        "[F>;"
    }
.end annotation


# direct methods
.method constructor <init>(Z)V
    .locals 0

    .line 479
    invoke-direct {p0, p1}, Landroidx/navigation/NavType;-><init>(Z)V

    return-void
.end method


# virtual methods
.method public bridge synthetic get(Landroid/os/Bundle;Ljava/lang/String;)Ljava/lang/Object;
    .locals 0

    .line 479
    invoke-virtual {p0, p1, p2}, Landroidx/navigation/NavType$7;->get(Landroid/os/Bundle;Ljava/lang/String;)[F

    move-result-object p0

    return-object p0
.end method

.method public get(Landroid/os/Bundle;Ljava/lang/String;)[F
    .locals 0

    .line 487
    invoke-virtual {p1, p2}, Landroid/os/Bundle;->get(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, [F

    return-object p0
.end method

.method public getName()Ljava/lang/String;
    .locals 0

    const-string p0, "float[]"

    return-object p0
.end method

.method public bridge synthetic parseValue(Ljava/lang/String;)Ljava/lang/Object;
    .locals 0

    .line 479
    invoke-virtual {p0, p1}, Landroidx/navigation/NavType$7;->parseValue(Ljava/lang/String;)[F

    move-result-object p0

    return-object p0
.end method

.method public parseValue(Ljava/lang/String;)[F
    .locals 0

    .line 493
    new-instance p0, Ljava/lang/UnsupportedOperationException;

    const-string p1, "Arrays don\'t support default values."

    invoke-direct {p0, p1}, Ljava/lang/UnsupportedOperationException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public bridge synthetic put(Landroid/os/Bundle;Ljava/lang/String;Ljava/lang/Object;)V
    .locals 0

    .line 479
    check-cast p3, [F

    invoke-virtual {p0, p1, p2, p3}, Landroidx/navigation/NavType$7;->put(Landroid/os/Bundle;Ljava/lang/String;[F)V

    return-void
.end method

.method public put(Landroid/os/Bundle;Ljava/lang/String;[F)V
    .locals 0

    .line 482
    invoke-virtual {p1, p2, p3}, Landroid/os/Bundle;->putFloatArray(Ljava/lang/String;[F)V

    return-void
.end method
