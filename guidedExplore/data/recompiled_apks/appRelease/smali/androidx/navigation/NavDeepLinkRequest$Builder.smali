.class public final Landroidx/navigation/NavDeepLinkRequest$Builder;
.super Ljava/lang/Object;
.source "NavDeepLinkRequest.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Landroidx/navigation/NavDeepLinkRequest;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x19
    name = "Builder"
.end annotation


# instance fields
.field private mAction:Ljava/lang/String;

.field private mMimeType:Ljava/lang/String;

.field private mUri:Landroid/net/Uri;


# direct methods
.method private constructor <init>()V
    .locals 0

    .line 116
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static fromAction(Ljava/lang/String;)Landroidx/navigation/NavDeepLinkRequest$Builder;
    .locals 1

    .line 141
    invoke-virtual {p0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_0

    .line 145
    new-instance v0, Landroidx/navigation/NavDeepLinkRequest$Builder;

    invoke-direct {v0}, Landroidx/navigation/NavDeepLinkRequest$Builder;-><init>()V

    .line 146
    invoke-virtual {v0, p0}, Landroidx/navigation/NavDeepLinkRequest$Builder;->setAction(Ljava/lang/String;)Landroidx/navigation/NavDeepLinkRequest$Builder;

    return-object v0

    .line 142
    :cond_0
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string v0, "The NavDeepLinkRequest cannot have an empty action."

    invoke-direct {p0, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public static fromMimeType(Ljava/lang/String;)Landroidx/navigation/NavDeepLinkRequest$Builder;
    .locals 1

    .line 158
    new-instance v0, Landroidx/navigation/NavDeepLinkRequest$Builder;

    invoke-direct {v0}, Landroidx/navigation/NavDeepLinkRequest$Builder;-><init>()V

    .line 159
    invoke-virtual {v0, p0}, Landroidx/navigation/NavDeepLinkRequest$Builder;->setMimeType(Ljava/lang/String;)Landroidx/navigation/NavDeepLinkRequest$Builder;

    return-object v0
.end method

.method public static fromUri(Landroid/net/Uri;)Landroidx/navigation/NavDeepLinkRequest$Builder;
    .locals 1

    .line 126
    new-instance v0, Landroidx/navigation/NavDeepLinkRequest$Builder;

    invoke-direct {v0}, Landroidx/navigation/NavDeepLinkRequest$Builder;-><init>()V

    .line 127
    invoke-virtual {v0, p0}, Landroidx/navigation/NavDeepLinkRequest$Builder;->setUri(Landroid/net/Uri;)Landroidx/navigation/NavDeepLinkRequest$Builder;

    return-object v0
.end method


# virtual methods
.method public build()Landroidx/navigation/NavDeepLinkRequest;
    .locals 3

    .line 226
    new-instance v0, Landroidx/navigation/NavDeepLinkRequest;

    iget-object v1, p0, Landroidx/navigation/NavDeepLinkRequest$Builder;->mUri:Landroid/net/Uri;

    iget-object v2, p0, Landroidx/navigation/NavDeepLinkRequest$Builder;->mAction:Ljava/lang/String;

    iget-object p0, p0, Landroidx/navigation/NavDeepLinkRequest$Builder;->mMimeType:Ljava/lang/String;

    invoke-direct {v0, v1, v2, p0}, Landroidx/navigation/NavDeepLinkRequest;-><init>(Landroid/net/Uri;Ljava/lang/String;Ljava/lang/String;)V

    return-object v0
.end method

.method public setAction(Ljava/lang/String;)Landroidx/navigation/NavDeepLinkRequest$Builder;
    .locals 1

    .line 187
    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_0

    .line 191
    iput-object p1, p0, Landroidx/navigation/NavDeepLinkRequest$Builder;->mAction:Ljava/lang/String;

    return-object p0

    .line 188
    :cond_0
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "The NavDeepLinkRequest cannot have an empty action."

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public setMimeType(Ljava/lang/String;)Landroidx/navigation/NavDeepLinkRequest$Builder;
    .locals 2

    const-string v0, "^[-\\w*.]+/[-\\w+*.]+$"

    .line 207
    invoke-static {v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;

    move-result-object v0

    .line 208
    invoke-virtual {v0, p1}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v0

    .line 210
    invoke-virtual {v0}, Ljava/util/regex/Matcher;->matches()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 215
    iput-object p1, p0, Landroidx/navigation/NavDeepLinkRequest$Builder;->mMimeType:Ljava/lang/String;

    return-object p0

    .line 211
    :cond_0
    new-instance p0, Ljava/lang/IllegalArgumentException;

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "The given mimeType "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string v0, " does not match to required \"type/subtype\" format"

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public setUri(Landroid/net/Uri;)Landroidx/navigation/NavDeepLinkRequest$Builder;
    .locals 0

    .line 172
    iput-object p1, p0, Landroidx/navigation/NavDeepLinkRequest$Builder;->mUri:Landroid/net/Uri;

    return-object p0
.end method
