# Preface

## Origin

This work began with a single, stubborn question — asked by someone with no formal training in theoretical physics,
and perhaps for that reason, unwilling to accept the standard answer.

The author's background is in systems engineering. Where a physicist sees a field equation, an engineer sees an
interface specification — and instinctively asks what is on the other side of it. Where a physicist accepts
renormalization as a valid technique, an engineer sees a patch on a leaking abstraction. Where a physicist adds a new
particle to explain an anomaly, an engineer asks whether the architecture is wrong.

This turned out to matter.

The question was this: if the rules governing reality are already complex enough to produce chemistry, biology,
consciousness, and galaxies, then the substrate underneath cannot be *more* complex than what emerges from it.
Complexity has to come from somewhere simpler. If the bottom layer is also complex, you need another layer beneath
that to explain it — and another, and another. That is not a foundation. That is an infinite regress with no floor.

So there must be a floor. And the floor must be almost embarrassingly simple — because everything above it already
accounts for all the complexity we observe. The question is not whether such a floor exists. The question is: what is
its single operation?

---

## The Engineering Insight

There is a principle every systems engineer learns, usually the hard way:

**Any shortcut eventually forces you back to proper design — no matter how clever the shortcut seemed.**

You can defer the correct architecture. You can patch around the missing abstraction layer. You can hardcode the
interface, add the special case, rename the infinity, postulate the undetected particle. The system will appear to
work. For a while.

But the debt accumulates. And eventually — always — the universe demands proper design.

Look at where theoretical physics stands in early 2026:

- Quantum field theory produces infinities. The response was renormalization — a mathematically sophisticated
  procedure for subtracting infinities from infinities to obtain finite predictions. It works with extraordinary
  precision. It is also, in an engineering sense, a patch [Weinberg, 1989].

- Galactic rotation curves do not match predictions from visible matter alone [Rubin & Ford, 1970]. The response was
  dark matter — a new, undetected form of matter postulated to make the numbers work. After five decades of
  searching, it has not been directly observed.

- The expansion of the universe was found to be accelerating. The response was the cosmological constant — a term
  Einstein had introduced and abandoned, now resurrected as "dark energy" and fixed at a precise value. The Dark
  Energy Spectroscopic Instrument has now measured, across more than 14 million galaxies, that this constant is not
  constant. The DESI DR2 results state explicitly: *"it is clear that ΛCDM is being challenged"* [DESI
  Collaboration, 2025].

- The fundamental forces refuse to unify within four dimensions. The response was string theory — a framework
  requiring six or seven additional spatial dimensions, compactified at scales too small to observe [Polchinski,
  1998]. After decades of theoretical development, it has produced no testable predictions that distinguish it from
  alternatives.

Each of these was a genuine intellectual achievement. Each one was also a shortcut around the same underlying
question: *what is the substrate?* Each one deferred that question rather than answering it. And now, as the DESI
results land alongside mounting tensions across the standard cosmological model, the accumulated debt is coming due
simultaneously.

A systems engineer looks at this situation and recognises it immediately. The abstraction layer is leaking. No amount
of patching at the application layer fixes a broken foundation. You have to go deeper.

This paper is an attempt to go deeper.

---

## Three Concepts: Substrate, Visualization, and "Simulation"

The initial question — *is the universe a simulation?* — turns out to be the wrong question. But it was the right
starting point, because unpacking why it is wrong leads directly to the framework this paper develops.

The simulation hypothesis, most formally stated by Bostrom [2003], asks whether the physical world we inhabit might
be a computation running on some external substrate. This is a serious philosophical question, but it smuggles in an
assumption: that "simulation" and "reality" are opposites — that if the universe is computational, it is somehow
less real. This assumption is what needs to be examined.

We propose three concepts that dissolve the confusion:

**Substrate** is the process that actually exists. In the framework we develop, this is the append-only monotonic
operation: the irreversible accumulation of state, one tick at a time. It has no geometry, no colour, no dimension,
no appearance. It simply is. It is as real as anything can be — it is the irreducible process from which everything
else follows. Crucially, it must be computable on finite-state machinery — not because the universe is a computer,
but because a truly primitive operation cannot require more machinery than existence itself to execute [Wheeler,
1990; Lloyd, 2000; Turing, 1936].

**Visualization** is what any observer constructs by reading a path through the accumulated substrate state. It can
be continuous, curved, probabilistic, apparently infinite. It is also real — it is the genuine experience of an
observer embedded in the process. It is not fake. It is not "merely" a rendering. It is physics as experienced from
inside.

**"Simulation"** — in quotation marks — is the confusion between these two layers. The question "is it a
simulation?" assumes that substrate and visualization are in competition, that one is real and the other is not.
They are not in competition. They are different levels of description of the same thing. The substrate is what the
universe *does*. The visualization is what it *looks like* from inside.

This three-part distinction is not new in spirit. Wheeler's "it from bit" [1990] argued that information is
primary. Zuse [1969] proposed that the universe computes itself. Wolfram [2002, 2020] built computational models
from simple rules. 't Hooft [2014] derived quantum mechanics from a cellular automaton substrate. What we add is
the precise separation of substrate from visualization, and the identification of the single substrate operation.

---

## What This Paper Is Not

This paper does not claim to replace quantum mechanics or general relativity.

Those theories are not wrong. They are extraordinarily precise descriptions of how the visualization behaves —
descriptions that will remain valid at every scale and regime where they have been tested. We have no interest in
competing with them.

What we are asking is a different question: *what substrate produces a visualization that those theories describe so
accurately?* If we are right, QM and GR do not become wrong — they become emergent descriptions of a deeper layer.
The relationship is the same as between thermodynamics and statistical mechanics. The higher-level description
remains valid. The lower-level description explains why.

There is one exception. In §4 we identify a specific experimental regime — interferometry with which-path
information — where the substrate theory makes a prediction that diverges from standard quantum mechanics. This is
not a claim that QM is wrong. It is the identification of a regime where the two descriptions can be distinguished
experimentally [Nimmrichter & Hornberger, 2013]. That is how substrate theories must be tested — not by replacing
the existing formalism, but by finding the places where the substrate peeks through.

---

## A Note on Method

This framework was developed computationally rather than analytically. The approach was deliberately inductive:
build the simplest possible substrate, observe what emerges, and let the behaviour generate the theory. Equations
came after phenomena, not before.

This is unusual in theoretical physics but entirely normal in engineering. Several results reported here were not
predicted — they emerged from the simulation and surprised us. We regard genuine surprise as evidence of discovery
rather than confirmation of prior assumptions. The most striking example: Pauli exclusion emerged from cell capacity
limits without being programmed, in a system that had no knowledge of quantum mechanics [exp_55].

Where results are validated, we say so with the evidence. Where results are speculative, we say so explicitly. The
reader is directed to `docs/theory/honest_status.md` in the accompanying repository for a continuously updated
assessment of what is confirmed, what is preliminary, and what remains open. We take falsifiability seriously
[Popper, 1959]: the interferometry prediction in §4 is designed to be wrong if the substrate theory is wrong.

---

## A Note on Collaboration

This work would not exist in its current form without an extended collaboration with Claude (Anthropic), used
throughout as a theoretical reasoning partner. All simulations, experimental results, and core physical intuitions
originate with the author. The AI contributed to formalization, consistency checking, and synthesis of the
theoretical framework.

At the author's request, the AI was asked directly: *if you were to propose a theory of everything from first
principles, unprompted, what would it look like?* That response appears in Appendix A. The reader may find it either
reassuring or unsettling that the answer it gave was, in most essential respects, what we had already built.

The AI had previously stated that a theory of everything would require entirely new mathematics. It took a stubborn
engineer three months to demonstrate that it required one fewer arithmetic operation than we currently use.

The full codebase, experimental logs, and theory documents are available at [repository URL].

---

*Tom Novak, March 2026*

---

## References

- [Bostrom, 2003] Bostrom, N. *Are You Living in a Computer Simulation?* Philosophical Quarterly 53, 243–255.
- [Carroll, 2004] Carroll, S. *Spacetime and Geometry.* Addison-Wesley.
- [DESI Collaboration, 2025] Abdul-Karim, M. et al. *DESI DR2 Results II.* arXiv:2503.14738.
- [Lloyd, 2000] Lloyd, S. *Ultimate Physical Limits to Computation.* Nature 406, 1047–1054.
- [Nimmrichter & Hornberger, 2013] *Macroscopicity of Mechanical Quantum Superposition States.* PRL 110, 160403.
- [Polchinski, 1998] Polchinski, J. *String Theory.* Cambridge University Press.
- [Popper, 1959] Popper, K. R. *The Logic of Scientific Discovery.* Hutchinson.
- [Rubin & Ford, 1970] Rubin, V. C., & Ford, W. K. *Rotation of the Andromeda Nebula.* ApJ 159, 379.
- ['t Hooft, 2014] 't Hooft, G. *The Cellular Automaton Interpretation of Quantum Mechanics.* Springer.
- [Turing, 1936] Turing, A. M. *On Computable Numbers.* Proc. London Math. Soc. 42, 230–265.
- [Weinberg, 1989] Weinberg, S. *The Cosmological Constant Problem.* Rev. Mod. Phys. 61, 1–23.
- [Wheeler, 1990] Wheeler, J. A. *Information, Physics, Quantum: The Search for Links.* Addison-Wesley.
- [Wolfram, 2002] Wolfram, S. *A New Kind of Science.* Wolfram Media.
- [Wolfram, 2020] Wolfram, S. *A Class of Models with the Potential to Represent Fundamental Physics.* Complex Systems 29.
- [Zuse, 1969] Zuse, K. *Rechnender Raum.* Vieweg.
