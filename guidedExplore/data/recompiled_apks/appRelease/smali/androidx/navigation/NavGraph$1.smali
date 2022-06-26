.class Landroidx/navigation/NavGraph$1;
.super Ljava/lang/Object;
.source "NavGraph.java"

# interfaces
.implements Ljava/util/Iterator;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Landroidx/navigation/NavGraph;->iterator()Ljava/util/Iterator;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Ljava/util/Iterator<",
        "Landroidx/navigation/NavDestination;",
        ">;"
    }
.end annotation


# instance fields
.field private mIndex:I

.field private mWentToNext:Z

.field final synthetic this$0:Landroidx/navigation/NavGraph;


# direct methods
.method constructor <init>(Landroidx/navigation/NavGraph;)V
    .locals 0

    .line 187
    iput-object p1, p0, Landroidx/navigation/NavGraph$1;->this$0:Landroidx/navigation/NavGraph;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    const/4 p1, -0x1

    .line 188
    iput p1, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    const/4 p1, 0x0

    .line 189
    iput-boolean p1, p0, Landroidx/navigation/NavGraph$1;->mWentToNext:Z

    return-void
.end method


# virtual methods
.method public hasNext()Z
    .locals 2

    .line 193
    iget v0, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    const/4 v1, 0x1

    add-int/2addr v0, v1

    iget-object p0, p0, Landroidx/navigation/NavGraph$1;->this$0:Landroidx/navigation/NavGraph;

    iget-object p0, p0, Landroidx/navigation/NavGraph;->mNodes:Landroidx/collection/SparseArrayCompat;

    invoke-virtual {p0}, Landroidx/collection/SparseArrayCompat;->size()I

    move-result p0

    if-ge v0, p0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v1, 0x0

    :goto_0
    return v1
.end method

.method public next()Landroidx/navigation/NavDestination;
    .locals 3

    .line 198
    invoke-virtual {p0}, Landroidx/navigation/NavGraph$1;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_0

    const/4 v0, 0x1

    .line 201
    iput-boolean v0, p0, Landroidx/navigation/NavGraph$1;->mWentToNext:Z

    .line 202
    iget-object v1, p0, Landroidx/navigation/NavGraph$1;->this$0:Landroidx/navigation/NavGraph;

    iget-object v1, v1, Landroidx/navigation/NavGraph;->mNodes:Landroidx/collection/SparseArrayCompat;

    iget v2, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    add-int/2addr v2, v0

    iput v2, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    invoke-virtual {v1, v2}, Landroidx/collection/SparseArrayCompat;->valueAt(I)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Landroidx/navigation/NavDestination;

    return-object p0

    .line 199
    :cond_0
    new-instance p0, Ljava/util/NoSuchElementException;

    invoke-direct {p0}, Ljava/util/NoSuchElementException;-><init>()V

    throw p0
.end method

.method public bridge synthetic next()Ljava/lang/Object;
    .locals 0

    .line 187
    invoke-virtual {p0}, Landroidx/navigation/NavGraph$1;->next()Landroidx/navigation/NavDestination;

    move-result-object p0

    return-object p0
.end method

.method public remove()V
    .locals 2

    .line 207
    iget-boolean v0, p0, Landroidx/navigation/NavGraph$1;->mWentToNext:Z

    if-eqz v0, :cond_0

    .line 211
    iget-object v0, p0, Landroidx/navigation/NavGraph$1;->this$0:Landroidx/navigation/NavGraph;

    iget-object v0, v0, Landroidx/navigation/NavGraph;->mNodes:Landroidx/collection/SparseArrayCompat;

    iget v1, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    invoke-virtual {v0, v1}, Landroidx/collection/SparseArrayCompat;->valueAt(I)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroidx/navigation/NavDestination;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroidx/navigation/NavDestination;->setParent(Landroidx/navigation/NavGraph;)V

    .line 212
    iget-object v0, p0, Landroidx/navigation/NavGraph$1;->this$0:Landroidx/navigation/NavGraph;

    iget-object v0, v0, Landroidx/navigation/NavGraph;->mNodes:Landroidx/collection/SparseArrayCompat;

    iget v1, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    invoke-virtual {v0, v1}, Landroidx/collection/SparseArrayCompat;->removeAt(I)V

    .line 213
    iget v0, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    add-int/lit8 v0, v0, -0x1

    iput v0, p0, Landroidx/navigation/NavGraph$1;->mIndex:I

    const/4 v0, 0x0

    .line 214
    iput-boolean v0, p0, Landroidx/navigation/NavGraph$1;->mWentToNext:Z

    return-void

    .line 208
    :cond_0
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string v0, "You must call next() before you can remove an element"

    invoke-direct {p0, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method
