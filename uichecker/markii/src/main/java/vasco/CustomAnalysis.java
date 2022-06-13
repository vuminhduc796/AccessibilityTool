/*
 * Copyright (c) 2020. Zhen Zhang
 */

package vasco;

import java.util.List;
import java.util.Set;

public abstract class CustomAnalysis<M,N,A> extends ForwardInterProceduralAnalysis<M,N,A> {
    /**
     * {@inheritDoc}
     */
    @Override
    public void doAnalysis() {

        // Initial contexts
        for (M method : programRepresentation().getEntryPoints()) {
            if (programRepresentation().isPhantomMethod(method)) {
                initContextForPhantomMethod(method, boundaryValue(method));
            } else {
                initContext(method, boundaryValue(method));
            }
        }

        // Perform work-list based analysis
        while (!worklist.isEmpty()) {
            // Get the newest context on the work-list
            VascoContext<M, N, A> currentContext = worklist.last();

            // If this context has no more nodes to analyze, then take it out of the work-list
            if (currentContext.getWorkList().isEmpty()) {
                currentContext.markAnalysed();
                worklist.remove(currentContext);
                continue;
            }


            // Remove the next node to process from the context's work-list
            N node = currentContext.getWorkList().pollFirst();

            if (node != null) {
                // Compute the IN data flow value (only for non-entry units).
                List<N> predecessors = currentContext.getControlFlowGraph().getPredsOf(node);
                if (predecessors.size() != 0) {
                    // Initialise to the TOP value
                    A in = topValue();
                    // Merge OUT values of all predecessors
                    for (N pred : predecessors) {
                        A predOut = currentContext.getValueAfter(pred);
                        in = meet(in, predOut);
                    }
                    // Set the IN value at the node to the result
                    currentContext.setValueBefore(node, in);
                }

                // Store the value of OUT before the flow function is processed.
                A prevOut = currentContext.getValueAfter(node);

                // Get the value of IN
                A in = currentContext.getValueBefore(node);

                if (verbose) {
                    System.out.println("IN = " + in);
                    System.err.println(node);
                }

                // Now to compute the OUT value
                A out;

                // Handle flow functions depending on whether this is a call statement or not
                if (programRepresentation().isCall(node)) {

                    out = topValue();
                    boolean hit = false;
                    if (!programRepresentation().resolveTargets(currentContext.getMethod(), node).isEmpty()) {
                        for (M targetMethod : programRepresentation().resolveTargets(currentContext.getMethod(), node)) {
                            A entryValue = callEntryFlowFunction(currentContext, targetMethod, node, in);

                            CallSite<M, N, A> callSite = new CallSite<M, N, A>(currentContext, node);

                            // Check if the called method has a context associated with this entry flow:
                            VascoContext<M, N, A> targetContext = getContext(targetMethod, entryValue);
                            // If not, then set 'targetContext' to a new context with the given entry flow.
                            if (targetContext == null) {
                                targetContext = initContext(targetMethod, entryValue);
                                if (verbose) {
                                    System.out.println("[NEW] X" + currentContext + " -> X" + targetContext + " " + targetMethod + " ");
                                    System.out.println("ENTRY(X" + targetContext + ") = " + entryValue);
                                }

                            }

                            // Store the transition from the calling context and site to the called context.
                            contextTransitions.addTransition(callSite, targetContext);

                            // Check if the target context has been analysed (surely not if it is just newly made):
                            if (targetContext.isAnalysed()) {
                                hit = true;
                                A exitValue = targetContext.getExitValue();
                                if (verbose) {
                                    System.out.println("[HIT] X" + currentContext + " -> X" + targetContext + " " + targetMethod + " ");
                                    System.out.println("EXIT(X" + targetContext + ") = " + exitValue);
                                }
                                A returnedValue = callExitFlowFunction(currentContext, targetMethod, node, exitValue);
                                out = meet(out, returnedValue);
                            }
                        }

                        // If there was at least one hit, continue propagation
                        if (hit) {
//                            A localValue = callLocalFlowFunction(currentContext, node, in);
                            out = meetAssign(in, out);
                        } else {
                            out = callLocalFlowFunction(currentContext, node, in);
                        }
                    } else {
                        // handle phantom method
                        out = callLocalFlowFunction(currentContext, node, in);
                    }
                } else {
                    out = normalFlowFunction(currentContext, node, in);
                }
                if (verbose) {
                    System.out.println("OUT = " + out);
                    System.out.println("---------------------------------------");
                }


                // Merge with previous OUT to force monotonicity (harmless if flow functions are monotinic)
                out = meet(out, prevOut);

                // Set the OUT value
                currentContext.setValueAfter(node, out);

                // If OUT has changed...
                if (out.equals(prevOut) == false) {
                    // Then add successors to the work-list.
                    for (N successor : currentContext.getControlFlowGraph().getSuccsOf(node)) {
                        currentContext.getWorkList().add(successor);
                    }
                }
                // If the unit is in TAILS, then we have at least one
                // path to the end of the method, so add the NULL unit
                if (currentContext.getControlFlowGraph().getTails().contains(node)) {
                    currentContext.getWorkList().add(null);
                }
            } else {
                // NULL unit, which means the end of the method.
                assert (currentContext.getWorkList().isEmpty());

                // Exit value is the merge of the OUTs of the tail nodes.
                A exitValue = topValue();
                for (N tailNode : currentContext.getControlFlowGraph().getTails()) {
                    A tailOut = currentContext.getValueAfter(tailNode);
                    exitValue = meet(exitValue, tailOut);
                }

                // Set the exit value of the context.
                currentContext.setExitValue(exitValue);

                // Mark this context as analysed at least once.
                currentContext.markAnalysed();

                // Add callers to work-list, if any
                Set<CallSite<M, N, A>> callers = contextTransitions.getCallers(currentContext);
                if (callers != null) {
                    for (CallSite<M, N, A> callSite : callers) {
                        // Extract the calling context and node from the caller site.
                        VascoContext<M, N, A> callingContext = callSite.getCallingContext();
                        N callNode = callSite.getCallNode();
                        // Add the calling unit to the calling context's node work-list.
                        callingContext.getWorkList().add(callNode);
                        // Ensure that the calling context is on the context work-list.
                        worklist.add(callingContext);
                    }
                }

                // Free memory on-the-fly if not needed
                if (freeResultsOnTheFly) {
                    Set<VascoContext<M, N, A>> reachableContexts = contextTransitions.reachableSet(currentContext, true);
                    // If any reachable contexts exist on the work-list, then we cannot free memory
                    boolean canFree = true;
                    for (VascoContext<M, N, A> reachableContext : reachableContexts) {
                        if (worklist.contains(reachableContext)) {
                            canFree = false;
                            break;
                        }
                    }
                    // If no reachable contexts on the stack, then free memory associated
                    // with this context
                    if (canFree) {
                        for (VascoContext<M, N, A> reachableContext : reachableContexts) {
                            reachableContext.freeMemory();
                        }
                    }
                }
            }

        }

        // Sanity check
        for (List<VascoContext<M, N, A>> contextList : contexts.values()) {
            for (VascoContext<M, N, A> context : contextList) {
                if (context.isAnalysed() == false) {
                    System.err.println("*** ATTENTION ***: Only partial analysis of X" + context +
                            " " + context.getMethod());
                }
            }
        }
    }

    public abstract A meetAssign(A op1, A op2);
}
