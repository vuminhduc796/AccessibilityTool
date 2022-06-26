.class public Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
.super Ljava/lang/Object;
.source "ShortcutInfoCompat.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Landroidx/core/content/pm/ShortcutInfoCompat;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x9
    name = "Builder"
.end annotation


# instance fields
.field private final mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

.field private mIsConversation:Z


# direct methods
.method public constructor <init>(Landroid/content/Context;Landroid/content/pm/ShortcutInfo;)V
    .locals 1

    .line 545
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 546
    new-instance v0, Landroidx/core/content/pm/ShortcutInfoCompat;

    invoke-direct {v0}, Landroidx/core/content/pm/ShortcutInfoCompat;-><init>()V

    iput-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    .line 547
    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mContext:Landroid/content/Context;

    .line 548
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getId()Ljava/lang/String;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mId:Ljava/lang/String;

    .line 549
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getPackage()Ljava/lang/String;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mPackageName:Ljava/lang/String;

    .line 550
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getIntents()[Landroid/content/Intent;

    move-result-object p0

    .line 551
    array-length p1, p0

    invoke-static {p0, p1}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object p0

    check-cast p0, [Landroid/content/Intent;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    .line 552
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getActivity()Landroid/content/ComponentName;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mActivity:Landroid/content/ComponentName;

    .line 553
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getShortLabel()Ljava/lang/CharSequence;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLabel:Ljava/lang/CharSequence;

    .line 554
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getLongLabel()Ljava/lang/CharSequence;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLongLabel:Ljava/lang/CharSequence;

    .line 555
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getDisabledMessage()Ljava/lang/CharSequence;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledMessage:Ljava/lang/CharSequence;

    .line 556
    sget p0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 p1, 0x1c

    if-lt p0, p1, :cond_0

    .line 557
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getDisabledReason()I

    move-result p0

    iput p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledReason:I

    goto :goto_1

    .line 559
    :cond_0
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isEnabled()Z

    move-result p0

    if-eqz p0, :cond_1

    const/4 p0, 0x0

    goto :goto_0

    :cond_1
    const/4 p0, 0x3

    .line 561
    :goto_0
    iput p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledReason:I

    .line 563
    :goto_1
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getCategories()Ljava/util/Set;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mCategories:Ljava/util/Set;

    .line 564
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getExtras()Landroid/os/PersistableBundle;

    move-result-object p0

    invoke-static {p0}, Landroidx/core/content/pm/ShortcutInfoCompat;->getPersonsFromExtra(Landroid/os/PersistableBundle;)[Landroidx/core/app/Person;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mPersons:[Landroidx/core/app/Person;

    .line 565
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getUserHandle()Landroid/os/UserHandle;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mUser:Landroid/os/UserHandle;

    .line 566
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getLastChangedTimestamp()J

    move-result-wide p0

    iput-wide p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLastChangedTimestamp:J

    .line 567
    sget p0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 p1, 0x1e

    if-lt p0, p1, :cond_2

    .line 568
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isCached()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsCached:Z

    .line 570
    :cond_2
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isDynamic()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsDynamic:Z

    .line 571
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isPinned()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsPinned:Z

    .line 572
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isDeclaredInManifest()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsDeclaredInManifest:Z

    .line 573
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isImmutable()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsImmutable:Z

    .line 574
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->isEnabled()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsEnabled:Z

    .line 575
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->hasKeyFieldsOnly()Z

    move-result p0

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mHasKeyFieldsOnly:Z

    .line 576
    invoke-static {p2}, Landroidx/core/content/pm/ShortcutInfoCompat;->getLocusId(Landroid/content/pm/ShortcutInfo;)Landroidx/core/content/LocusIdCompat;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLocusId:Landroidx/core/content/LocusIdCompat;

    .line 577
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getRank()I

    move-result p0

    iput p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mRank:I

    .line 578
    invoke-virtual {p2}, Landroid/content/pm/ShortcutInfo;->getExtras()Landroid/os/PersistableBundle;

    move-result-object p0

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mExtras:Landroid/os/PersistableBundle;

    return-void
.end method

.method public constructor <init>(Landroid/content/Context;Ljava/lang/String;)V
    .locals 1

    .line 494
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 495
    new-instance v0, Landroidx/core/content/pm/ShortcutInfoCompat;

    invoke-direct {v0}, Landroidx/core/content/pm/ShortcutInfoCompat;-><init>()V

    iput-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    .line 496
    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mContext:Landroid/content/Context;

    .line 497
    iput-object p2, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mId:Ljava/lang/String;

    return-void
.end method

.method public constructor <init>(Landroidx/core/content/pm/ShortcutInfoCompat;)V
    .locals 3

    .line 504
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 505
    new-instance v0, Landroidx/core/content/pm/ShortcutInfoCompat;

    invoke-direct {v0}, Landroidx/core/content/pm/ShortcutInfoCompat;-><init>()V

    iput-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    .line 506
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mContext:Landroid/content/Context;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mContext:Landroid/content/Context;

    .line 507
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mId:Ljava/lang/String;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mId:Ljava/lang/String;

    .line 508
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mPackageName:Ljava/lang/String;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mPackageName:Ljava/lang/String;

    .line 509
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    iget-object v1, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    array-length v1, v1

    invoke-static {p0, v1}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object p0

    check-cast p0, [Landroid/content/Intent;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    .line 510
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mActivity:Landroid/content/ComponentName;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mActivity:Landroid/content/ComponentName;

    .line 511
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mLabel:Ljava/lang/CharSequence;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLabel:Ljava/lang/CharSequence;

    .line 512
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mLongLabel:Ljava/lang/CharSequence;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLongLabel:Ljava/lang/CharSequence;

    .line 513
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledMessage:Ljava/lang/CharSequence;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledMessage:Ljava/lang/CharSequence;

    .line 514
    iget p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledReason:I

    iput p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledReason:I

    .line 515
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIcon:Landroidx/core/graphics/drawable/IconCompat;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIcon:Landroidx/core/graphics/drawable/IconCompat;

    .line 516
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsAlwaysBadged:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsAlwaysBadged:Z

    .line 517
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mUser:Landroid/os/UserHandle;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mUser:Landroid/os/UserHandle;

    .line 518
    iget-wide v1, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mLastChangedTimestamp:J

    iput-wide v1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLastChangedTimestamp:J

    .line 519
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsCached:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsCached:Z

    .line 520
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsDynamic:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsDynamic:Z

    .line 521
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsPinned:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsPinned:Z

    .line 522
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsDeclaredInManifest:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsDeclaredInManifest:Z

    .line 523
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsImmutable:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsImmutable:Z

    .line 524
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsEnabled:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsEnabled:Z

    .line 525
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mLocusId:Landroidx/core/content/LocusIdCompat;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLocusId:Landroidx/core/content/LocusIdCompat;

    .line 526
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsLongLived:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsLongLived:Z

    .line 527
    iget-boolean p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mHasKeyFieldsOnly:Z

    iput-boolean p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mHasKeyFieldsOnly:Z

    .line 528
    iget p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mRank:I

    iput p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mRank:I

    .line 529
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mPersons:[Landroidx/core/app/Person;

    if-eqz p0, :cond_0

    .line 530
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mPersons:[Landroidx/core/app/Person;

    iget-object v1, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mPersons:[Landroidx/core/app/Person;

    array-length v1, v1

    invoke-static {p0, v1}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object p0

    check-cast p0, [Landroidx/core/app/Person;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mPersons:[Landroidx/core/app/Person;

    .line 532
    :cond_0
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mCategories:Ljava/util/Set;

    if-eqz p0, :cond_1

    .line 533
    new-instance p0, Ljava/util/HashSet;

    iget-object v1, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mCategories:Ljava/util/Set;

    invoke-direct {p0, v1}, Ljava/util/HashSet;-><init>(Ljava/util/Collection;)V

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mCategories:Ljava/util/Set;

    .line 535
    :cond_1
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mExtras:Landroid/os/PersistableBundle;

    if-eqz p0, :cond_2

    .line 536
    iget-object p0, p1, Landroidx/core/content/pm/ShortcutInfoCompat;->mExtras:Landroid/os/PersistableBundle;

    iput-object p0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mExtras:Landroid/os/PersistableBundle;

    :cond_2
    return-void
.end method


# virtual methods
.method public build()Landroidx/core/content/pm/ShortcutInfoCompat;
    .locals 3

    .line 810
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iget-object v0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLabel:Ljava/lang/CharSequence;

    invoke-static {v0}, Landroid/text/TextUtils;->isEmpty(Ljava/lang/CharSequence;)Z

    move-result v0

    if-nez v0, :cond_3

    .line 813
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iget-object v0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    if-eqz v0, :cond_2

    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iget-object v0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    array-length v0, v0

    if-eqz v0, :cond_2

    .line 816
    iget-boolean v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mIsConversation:Z

    if-eqz v0, :cond_1

    .line 817
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iget-object v0, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLocusId:Landroidx/core/content/LocusIdCompat;

    if-nez v0, :cond_0

    .line 818
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    new-instance v1, Landroidx/core/content/LocusIdCompat;

    iget-object v2, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iget-object v2, v2, Landroidx/core/content/pm/ShortcutInfoCompat;->mId:Ljava/lang/String;

    invoke-direct {v1, v2}, Landroidx/core/content/LocusIdCompat;-><init>(Ljava/lang/String;)V

    iput-object v1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLocusId:Landroidx/core/content/LocusIdCompat;

    .line 820
    :cond_0
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    const/4 v1, 0x1

    iput-boolean v1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsLongLived:Z

    .line 822
    :cond_1
    iget-object p0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    return-object p0

    .line 814
    :cond_2
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string v0, "Shortcut must have an intent"

    invoke-direct {p0, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 811
    :cond_3
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string v0, "Shortcut must have a non-empty label"

    invoke-direct {p0, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public setActivity(Landroid/content/ComponentName;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 696
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mActivity:Landroid/content/ComponentName;

    return-object p0
.end method

.method public setAlwaysBadged()Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 2

    .line 714
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    const/4 v1, 0x1

    iput-boolean v1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsAlwaysBadged:Z

    return-object p0
.end method

.method public setCategories(Ljava/util/Set;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/Set<",
            "Ljava/lang/String;",
            ">;)",
            "Landroidx/core/content/pm/ShortcutInfoCompat$Builder;"
        }
    .end annotation

    .line 753
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mCategories:Ljava/util/Set;

    return-object p0
.end method

.method public setDisabledMessage(Ljava/lang/CharSequence;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 618
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mDisabledMessage:Ljava/lang/CharSequence;

    return-object p0
.end method

.method public setExtras(Landroid/os/PersistableBundle;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 800
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mExtras:Landroid/os/PersistableBundle;

    return-object p0
.end method

.method public setIcon(Landroidx/core/graphics/drawable/IconCompat;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 653
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIcon:Landroidx/core/graphics/drawable/IconCompat;

    return-object p0
.end method

.method public setIntent(Landroid/content/Intent;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 2

    const/4 v0, 0x1

    new-array v0, v0, [Landroid/content/Intent;

    const/4 v1, 0x0

    aput-object p1, v0, v1

    .line 633
    invoke-virtual {p0, v0}, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->setIntents([Landroid/content/Intent;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;

    move-result-object p0

    return-object p0
.end method

.method public setIntents([Landroid/content/Intent;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 644
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIntents:[Landroid/content/Intent;

    return-object p0
.end method

.method public setIsConversation()Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    const/4 v0, 0x1

    .line 683
    iput-boolean v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mIsConversation:Z

    return-object p0
.end method

.method public setLocusId(Landroidx/core/content/LocusIdCompat;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 667
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLocusId:Landroidx/core/content/LocusIdCompat;

    return-object p0
.end method

.method public setLongLabel(Ljava/lang/CharSequence;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 606
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLongLabel:Ljava/lang/CharSequence;

    return-object p0
.end method

.method public setLongLived()Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 2
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation

    .line 763
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    const/4 v1, 0x1

    iput-boolean v1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsLongLived:Z

    return-object p0
.end method

.method public setLongLived(Z)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 774
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-boolean p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mIsLongLived:Z

    return-object p0
.end method

.method public setPerson(Landroidx/core/app/Person;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 2

    const/4 v0, 0x1

    new-array v0, v0, [Landroidx/core/app/Person;

    const/4 v1, 0x0

    aput-object p1, v0, v1

    .line 728
    invoke-virtual {p0, v0}, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->setPersons([Landroidx/core/app/Person;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;

    move-result-object p0

    return-object p0
.end method

.method public setPersons([Landroidx/core/app/Person;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 736
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mPersons:[Landroidx/core/app/Person;

    return-object p0
.end method

.method public setRank(I)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 786
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mRank:I

    return-object p0
.end method

.method public setShortLabel(Ljava/lang/CharSequence;)Landroidx/core/content/pm/ShortcutInfoCompat$Builder;
    .locals 1

    .line 592
    iget-object v0, p0, Landroidx/core/content/pm/ShortcutInfoCompat$Builder;->mInfo:Landroidx/core/content/pm/ShortcutInfoCompat;

    iput-object p1, v0, Landroidx/core/content/pm/ShortcutInfoCompat;->mLabel:Ljava/lang/CharSequence;

    return-object p0
.end method
