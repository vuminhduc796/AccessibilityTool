.class public Lcom/example/researchtestapp/MainActivity;
.super Landroidx/appcompat/app/AppCompatActivity;
.source "MainActivity.java"


# instance fields
.field private appBarConfiguration:Landroidx/navigation/ui/AppBarConfiguration;

.field private binding:Lcom/example/researchtestapp/databinding/ActivityMainBinding;


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 21
    invoke-direct {p0}, Landroidx/appcompat/app/AppCompatActivity;-><init>()V

    return-void
.end method


# virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2

    .line 28
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    .line 30
    invoke-virtual {p0}, Lcom/example/researchtestapp/MainActivity;->getLayoutInflater()Landroid/view/LayoutInflater;

    move-result-object p1

    invoke-static {p1}, Lcom/example/researchtestapp/databinding/ActivityMainBinding;->inflate(Landroid/view/LayoutInflater;)Lcom/example/researchtestapp/databinding/ActivityMainBinding;

    move-result-object p1

    iput-object p1, p0, Lcom/example/researchtestapp/MainActivity;->binding:Lcom/example/researchtestapp/databinding/ActivityMainBinding;

    .line 31
    invoke-virtual {p1}, Lcom/example/researchtestapp/databinding/ActivityMainBinding;->getRoot()Landroidx/coordinatorlayout/widget/CoordinatorLayout;

    move-result-object p1

    invoke-virtual {p0, p1}, Lcom/example/researchtestapp/MainActivity;->setContentView(Landroid/view/View;)V

    .line 33
    iget-object p1, p0, Lcom/example/researchtestapp/MainActivity;->binding:Lcom/example/researchtestapp/databinding/ActivityMainBinding;

    iget-object p1, p1, Lcom/example/researchtestapp/databinding/ActivityMainBinding;->toolbar:Landroidx/appcompat/widget/Toolbar;

    invoke-virtual {p0, p1}, Lcom/example/researchtestapp/MainActivity;->setSupportActionBar(Landroidx/appcompat/widget/Toolbar;)V

    const p1, 0x7f08010f

    .line 35
    invoke-static {p0, p1}, Landroidx/navigation/Navigation;->findNavController(Landroid/app/Activity;I)Landroidx/navigation/NavController;

    move-result-object p1

    .line 36
    new-instance v0, Landroidx/navigation/ui/AppBarConfiguration$Builder;

    invoke-virtual {p1}, Landroidx/navigation/NavController;->getGraph()Landroidx/navigation/NavGraph;

    move-result-object v1

    invoke-direct {v0, v1}, Landroidx/navigation/ui/AppBarConfiguration$Builder;-><init>(Landroidx/navigation/NavGraph;)V

    invoke-virtual {v0}, Landroidx/navigation/ui/AppBarConfiguration$Builder;->build()Landroidx/navigation/ui/AppBarConfiguration;

    move-result-object v0

    iput-object v0, p0, Lcom/example/researchtestapp/MainActivity;->appBarConfiguration:Landroidx/navigation/ui/AppBarConfiguration;

    .line 37
    invoke-static {p0, p1, v0}, Landroidx/navigation/ui/NavigationUI;->setupActionBarWithNavController(Landroidx/appcompat/app/AppCompatActivity;Landroidx/navigation/NavController;Landroidx/navigation/ui/AppBarConfiguration;)V

    .line 39
    iget-object p1, p0, Lcom/example/researchtestapp/MainActivity;->binding:Lcom/example/researchtestapp/databinding/ActivityMainBinding;

    iget-object p1, p1, Lcom/example/researchtestapp/databinding/ActivityMainBinding;->fab:Lcom/google/android/material/floatingactionbutton/FloatingActionButton;

    new-instance v0, Lcom/example/researchtestapp/MainActivity$1;

    invoke-direct {v0, p0}, Lcom/example/researchtestapp/MainActivity$1;-><init>(Lcom/example/researchtestapp/MainActivity;)V

    invoke-virtual {p1, v0}, Lcom/google/android/material/floatingactionbutton/FloatingActionButton;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    return-void
.end method

.method public onCreateOptionsMenu(Landroid/view/Menu;)Z
    .locals 1

    .line 51
    invoke-virtual {p0}, Lcom/example/researchtestapp/MainActivity;->getMenuInflater()Landroid/view/MenuInflater;

    move-result-object p0

    const/high16 v0, 0x7f0c0000

    invoke-virtual {p0, v0, p1}, Landroid/view/MenuInflater;->inflate(ILandroid/view/Menu;)V

    const/4 p0, 0x1

    return p0
.end method

.method public onOptionsItemSelected(Landroid/view/MenuItem;)Z
    .locals 2

    .line 60
    invoke-interface {p1}, Landroid/view/MenuItem;->getItemId()I

    move-result v0

    const v1, 0x7f080044

    if-ne v0, v1, :cond_0

    const/4 p0, 0x1

    return p0

    .line 67
    :cond_0
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onOptionsItemSelected(Landroid/view/MenuItem;)Z

    move-result p0

    return p0
.end method

.method public onSupportNavigateUp()Z
    .locals 2

    const v0, 0x7f08010f

    .line 72
    invoke-static {p0, v0}, Landroidx/navigation/Navigation;->findNavController(Landroid/app/Activity;I)Landroidx/navigation/NavController;

    move-result-object v0

    .line 73
    iget-object v1, p0, Lcom/example/researchtestapp/MainActivity;->appBarConfiguration:Landroidx/navigation/ui/AppBarConfiguration;

    invoke-static {v0, v1}, Landroidx/navigation/ui/NavigationUI;->navigateUp(Landroidx/navigation/NavController;Landroidx/navigation/ui/AppBarConfiguration;)Z

    move-result v0

    if-nez v0, :cond_1

    .line 74
    invoke-super {p0}, Landroidx/appcompat/app/AppCompatActivity;->onSupportNavigateUp()Z

    move-result p0

    if-eqz p0, :cond_0

    goto :goto_0

    :cond_0
    const/4 p0, 0x0

    goto :goto_1

    :cond_1
    :goto_0
    const/4 p0, 0x1

    :goto_1
    return p0
.end method
