.class Landroidx/navigation/NavDeepLink$ParamQuery;
.super Ljava/lang/Object;
.source "NavDeepLink.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Landroidx/navigation/NavDeepLink;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0xa
    name = "ParamQuery"
.end annotation


# instance fields
.field private mArguments:Ljava/util/ArrayList;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/ArrayList<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private mParamRegex:Ljava/lang/String;


# direct methods
.method constructor <init>()V
    .locals 1

    .line 319
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 320
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    iput-object v0, p0, Landroidx/navigation/NavDeepLink$ParamQuery;->mArguments:Ljava/util/ArrayList;

    return-void
.end method


# virtual methods
.method addArgumentName(Ljava/lang/String;)V
    .locals 0

    .line 332
    iget-object p0, p0, Landroidx/navigation/NavDeepLink$ParamQuery;->mArguments:Ljava/util/ArrayList;

    invoke-virtual {p0, p1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    return-void
.end method

.method getArgumentName(I)Ljava/lang/String;
    .locals 0

    .line 336
    iget-object p0, p0, Landroidx/navigation/NavDeepLink$ParamQuery;->mArguments:Ljava/util/ArrayList;

    invoke-virtual {p0, p1}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljava/lang/String;

    return-object p0
.end method

.method getParamRegex()Ljava/lang/String;
    .locals 0

    .line 328
    iget-object p0, p0, Landroidx/navigation/NavDeepLink$ParamQuery;->mParamRegex:Ljava/lang/String;

    return-object p0
.end method

.method setParamRegex(Ljava/lang/String;)V
    .locals 0

    .line 324
    iput-object p1, p0, Landroidx/navigation/NavDeepLink$ParamQuery;->mParamRegex:Ljava/lang/String;

    return-void
.end method

.method public size()I
    .locals 0

    .line 340
    iget-object p0, p0, Landroidx/navigation/NavDeepLink$ParamQuery;->mArguments:Ljava/util/ArrayList;

    invoke-virtual {p0}, Ljava/util/ArrayList;->size()I

    move-result p0

    return p0
.end method
