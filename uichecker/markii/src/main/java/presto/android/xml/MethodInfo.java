package presto.android.xml;

public class MethodInfo {
    private String methodName;
    private String file;

    public MethodInfo(String methodName, String file){
        this.methodName = methodName;
        this.file = file;
    }

    public String getName(){
        return this.methodName;
    }

    public String getFile(){
        return this.file;
    }

}
