/* This file was generated by SableCC (http://www.sablecc.org/). */

package soot.jimple.parser.node;

import soot.jimple.parser.analysis.*;

@SuppressWarnings("nls")
public final class AMultBinop extends PBinop
{
    private TMult _mult_;

    public AMultBinop()
    {
        // Constructor
    }

    public AMultBinop(
        @SuppressWarnings("hiding") TMult _mult_)
    {
        // Constructor
        setMult(_mult_);

    }

    @Override
    public Object clone()
    {
        return new AMultBinop(
            cloneNode(this._mult_));
    }

    @Override
    public void apply(Switch sw)
    {
        ((Analysis) sw).caseAMultBinop(this);
    }

    public TMult getMult()
    {
        return this._mult_;
    }

    public void setMult(TMult node)
    {
        if(this._mult_ != null)
        {
            this._mult_.parent(null);
        }

        if(node != null)
        {
            if(node.parent() != null)
            {
                node.parent().removeChild(node);
            }

            node.parent(this);
        }

        this._mult_ = node;
    }

    @Override
    public String toString()
    {
        return ""
            + toString(this._mult_);
    }

    @Override
    void removeChild(@SuppressWarnings("unused") Node child)
    {
        // Remove child
        if(this._mult_ == child)
        {
            this._mult_ = null;
            return;
        }

        throw new RuntimeException("Not a child.");
    }

    @Override
    void replaceChild(@SuppressWarnings("unused") Node oldChild, @SuppressWarnings("unused") Node newChild)
    {
        // Replace child
        if(this._mult_ == oldChild)
        {
            setMult((TMult) newChild);
            return;
        }

        throw new RuntimeException("Not a child.");
    }
}
