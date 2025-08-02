# Chapter 4: Noethers Theorem and Dirac Equation

<!-- LATEX_PROTECTION_START -->
<!-- This content contains protected LaTeX expressions -->
<!-- Enhanced LaTeX Plugin will process data-latex attributes -->


*Conversation from October 02, 2024*

## Message 1

Give me an article explaining the proof of Noether's theorem (not necessarily displaying the entire proof) and applying it to the example of the Dirac equation.

---

## Message 2

**Linking symmetries to conservation**

I'm thinking through Noether's theorem, which ties continuous symmetries of an action to conserved currents. This connection is particularly influential in field theory, linking symmetries with conserved quantities.

**Unraveling symmetries**

I'm connecting Noether's theorem to the Dirac equation. Noether's theorem identifies conserved currents from symmetries, like electric charge from global phase transformations, highlighting their interdependence and conservation laws.

---

## Message 3

**Noether's Theorem and Its Application to the Dirac Equation**

*Abstract*: Emmy Noether's theorem is a cornerstone of theoretical physics, linking symmetries and conservation laws in physical systems. This article provides an overview of Noether's theorem, outlines its proof, and demonstrates its application to the Dirac equation, highlighting the connection between symmetries and conserved currents in quantum field theory.

---

### Introduction

Symmetry principles play a fundamental role in modern physics. They not only simplify complex problems but also reveal deep insights into the laws governing physical phenomena. Emmy Noether's theorem, formulated in 1915 and published in 1918, provides a profound connection between continuous symmetries and conservation laws in Lagrangian mechanics and field theory. This theorem has far-reaching implications across classical mechanics, quantum mechanics, and quantum field theory.

In this article, we will explore Noether's theorem and apply it to the Dirac equation, a relativistic wave equation describing spin-½ particles such as electrons. By examining the symmetries of the Dirac Lagrangian, we will derive conserved currents associated with these symmetries, illustrating the power and elegance of Noether's theorem in theoretical physics.

---

### Noether's Theorem: An Overview

**Statement of Noether's Theorem**

In its most general form, Noether's theorem states:

*For every continuous differentiable symmetry of the action of a physical system, there exists a corresponding conserved quantity.*

This means that if the action integral remains invariant under a continuous transformation of the fields and coordinates, then there exists a conserved current associated with this symmetry.

**Mathematical Formulation**

Consider a Lagrangian density <span class="latex-inline" data-latex=" \mathcal{L}(\phi_i, \partial_\mu \phi_i, x^\mu) ">$ \mathcal{L}(\phi_i, \partial_\mu \phi_i, x^\mu) $</span> dependent on fields <span class="latex-inline" data-latex=" \phi_i ">$ \phi_i $</span>, their derivatives <span class="latex-inline" data-latex=" \partial_\mu \phi_i ">$ \partial_\mu \phi_i $</span>, and spacetime coordinates <span class="latex-inline" data-latex=" x^\mu ">$ x^\mu $</span>. If the action

<div class="latex-display" data-latex="
S = \int \mathcal{L} \, d^4x
">$$
S = \int \mathcal{L} \, d^4x
$$</div>

is invariant under a continuous transformation of the fields <span class="latex-inline" data-latex=" \phi_i \rightarrow \phi_i + \delta \phi_i ">$ \phi_i \rightarrow \phi_i + \delta \phi_i $</span> and coordinates <span class="latex-inline" data-latex=" x^\mu \rightarrow x^\mu + \delta x^\mu ">$ x^\mu \rightarrow x^\mu + \delta x^\mu $</span>, then there exists a conserved current <span class="latex-inline" data-latex=" J^\mu ">$ J^\mu $</span> such that

<div class="latex-display" data-latex="
\partial_\mu J^\mu = 0.
">$$
\partial_\mu J^\mu = 0.
$$</div>

**Outline of the Proof**

1. **Action Invariance**: Assume the action <span class="latex-inline" data-latex=" S ">$ S $</span> is invariant under the transformation, implying <span class="latex-inline" data-latex=" \delta S = 0 ">$ \delta S = 0 $</span>.

2. **Variation of the Action**: The variation of the action can be expressed as

   <div class="latex-display" data-latex="
   \delta S = \int \left( \frac{\partial \mathcal{L}}{\partial \phi_i} - \partial_\mu \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi_i)} \right) \delta \phi_i \, d^4x + \int \partial_\mu \left( \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi_i)} \delta \phi_i + \mathcal{L} \delta x^\mu \right) d^4x.
   ">$$
   \delta S = \int \left( \frac{\partial \mathcal{L}}{\partial \phi_i} - \partial_\mu \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi_i)} \right) \delta \phi_i \, d^4x + \int \partial_\mu \left( \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi_i)} \delta \phi_i + \mathcal{L} \delta x^\mu \right) d^4x.
   $$</div>

3. **Euler-Lagrange Equations**: The first term vanishes on-shell due to the Euler-Lagrange equations.

4. **Conserved Current**: The remaining surface term leads to the conservation law:

   <div class="latex-display" data-latex="
   \partial_\mu J^\mu = 0, \quad \text{where} \quad J^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi_i)} \delta \phi_i + \mathcal{L} \delta x^\mu.
   ">$$
   \partial_\mu J^\mu = 0, \quad \text{where} \quad J^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi_i)} \delta \phi_i + \mathcal{L} \delta x^\mu.
   $$</div>

This conserved current <span class="latex-inline" data-latex=" J^\mu ">$ J^\mu $</span> is associated with the continuous symmetry of the action.

---

### The Dirac Equation and Its Symmetries

**Dirac Lagrangian Density**

The Dirac equation describes relativistic spin-½ particles. The Dirac Lagrangian density is given by

<div class="latex-display" data-latex="
\mathcal{L} = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi,
">$$
\mathcal{L} = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi,
$$</div>

where:

- <span class="latex-inline" data-latex=" \psi ">$ \psi $</span> is the Dirac spinor field.
- <span class="latex-inline" data-latex=" \bar{\psi} = \psi^\dagger \gamma^0 ">$ \bar{\psi} = \psi^\dagger \gamma^0 $</span> is the Dirac adjoint.
- <span class="latex-inline" data-latex=" \gamma^\mu ">$ \gamma^\mu $</span> are the Dirac gamma matrices.
- <span class="latex-inline" data-latex=" m ">$ m $</span> is the mass of the particle.
- Natural units (<span class="latex-inline" data-latex=" \hbar = c = 1 ">$ \hbar = c = 1 $</span>) are used.

**Symmetries of the Dirac Lagrangian**

The Dirac Lagrangian possesses several continuous symmetries:

1. **Global U(1) Phase Symmetry**: The Lagrangian is invariant under the global phase transformation

   <div class="latex-display" data-latex="
   \psi \rightarrow e^{i\alpha} \psi, \quad \bar{\psi} \rightarrow e^{-i\alpha} \bar{\psi},
   ">$$
   \psi \rightarrow e^{i\alpha} \psi, \quad \bar{\psi} \rightarrow e^{-i\alpha} \bar{\psi},
   $$</div>

   where <span class="latex-inline" data-latex=" \alpha ">$ \alpha $</span> is a constant real parameter.

2. **Poincaré Symmetry**: Invariance under spacetime translations and Lorentz transformations.

In this article, we focus on the global U(1) symmetry and its associated conserved current.

---

### Applying Noether's Theorem to the Dirac Equation

**Variation Under Global U(1) Transformation**

Under an infinitesimal global U(1) transformation with <span class="latex-inline" data-latex=" \alpha \ll 1 ">$ \alpha \ll 1 $</span>:

<div class="latex-display" data-latex="
\delta \psi = i\alpha \psi, \quad \delta \bar{\psi} = -i\alpha \bar{\psi}.
">$$
\delta \psi = i\alpha \psi, \quad \delta \bar{\psi} = -i\alpha \bar{\psi}.
$$</div>

Since the transformation does not depend on spacetime coordinates (<span class="latex-inline" data-latex=" \delta x^\mu = 0 ">$ \delta x^\mu = 0 $</span>), the action remains invariant (<span class="latex-inline" data-latex=" \delta S = 0 ">$ \delta S = 0 $</span>).

**Computing the Conserved Current**

Using Noether's theorem, the conserved current is

<div class="latex-display" data-latex="
J^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} \delta \psi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} \delta \bar{\psi}.
">$$
J^\mu = \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} \delta \psi + \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} \delta \bar{\psi}.
$$</div>

Compute the derivatives:

1. **Derivatives of the Lagrangian Density**:

   - For <span class="latex-inline" data-latex=" \psi ">$ \psi $</span>:

     <div class="latex-display" data-latex="
     \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} = i\bar{\psi} \gamma^\mu.
     ">$$
     \frac{\partial \mathcal{L}}{\partial (\partial_\mu \psi)} = i\bar{\psi} \gamma^\mu.
     $$</div>

   - For <span class="latex-inline" data-latex=" \bar{\psi} ">$ \bar{\psi} $</span>:

     <div class="latex-display" data-latex="
     \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} = 0,
     ">$$
     \frac{\partial \mathcal{L}}{\partial (\partial_\mu \bar{\psi})} = 0,
     $$</div>

     since <span class="latex-inline" data-latex=" \mathcal{L} ">$ \mathcal{L} $</span> does not depend on <span class="latex-inline" data-latex=" \partial_\mu \bar{\psi} ">$ \partial_\mu \bar{\psi} $</span>.

2. **Compute <span class="latex-inline" data-latex=" J^\mu ">$ J^\mu $</span>**:

   <div class="latex-display" data-latex="
   J^\mu = i\bar{\psi} \gamma^\mu (i\alpha \psi) + 0 \cdot (-i\alpha \bar{\psi}) = -\alpha \bar{\psi} \gamma^\mu \psi.
   ">$$
   J^\mu = i\bar{\psi} \gamma^\mu (i\alpha \psi) + 0 \cdot (-i\alpha \bar{\psi}) = -\alpha \bar{\psi} \gamma^\mu \psi.
   $$</div>

   Ignoring the constant <span class="latex-inline" data-latex=" \alpha ">$ \alpha $</span> (since it's arbitrary), the conserved current is

   <div class="latex-display" data-latex="
   J^\mu = \bar{\psi} \gamma^\mu \psi.
   ">$$
   J^\mu = \bar{\psi} \gamma^\mu \psi.
   $$</div>

**Conservation Law**

Applying the Euler-Lagrange equations, the divergence of the current vanishes:

<div class="latex-display" data-latex="
\partial_\mu J^\mu = 0.
">$$
\partial_\mu J^\mu = 0.
$$</div>

This represents the conservation of electric charge in quantum electrodynamics (QED), where <span class="latex-inline" data-latex=" J^\mu ">$ J^\mu $</span> is the electromagnetic current density.

---

### Physical Interpretation

**Conserved Quantity**

The conserved current <span class="latex-inline" data-latex=" J^\mu = \bar{\psi} \gamma^\mu \psi ">$ J^\mu = \bar{\psi} \gamma^\mu \psi $</span> corresponds to the probability current density in the Dirac theory. Its time component <span class="latex-inline" data-latex=" J^0 = \psi^\dagger \psi ">$ J^0 = \psi^\dagger \psi $</span> represents the probability density, which is always positive-definite.

**Electric Charge Conservation**

In the context of QED, coupling the Dirac field to the electromagnetic field, the global U(1) symmetry becomes a local gauge symmetry. The conserved current <span class="latex-inline" data-latex=" J^\mu ">$ J^\mu $</span> couples to the electromagnetic field <span class="latex-inline" data-latex=" A_\mu ">$ A_\mu $</span>, leading to the interaction term <span class="latex-inline" data-latex=" -e\bar{\psi} \gamma^\mu \psi A_\mu ">$ -e\bar{\psi} \gamma^\mu \psi A_\mu $</span> in the Lagrangian. Here, <span class="latex-inline" data-latex=" e ">$ e $</span> is the electric charge.

---

### Conclusion

Noether's theorem provides a fundamental link between symmetries and conservation laws in physics. By applying the theorem to the Dirac equation, we derived the conserved current associated with the global U(1) phase symmetry. This conserved current corresponds to the conservation of electric charge, a cornerstone of electromagnetic theory.

The application to the Dirac equation illustrates how Noether's theorem operates within quantum field theory, connecting abstract mathematical symmetries to physically observable conserved quantities. This interplay between symmetry and conservation continues to be a guiding principle in the development of modern theoretical physics.

---

### References

1. **Noether, E.** (1918). *Invariante Variationsprobleme*. Nachr. d. König. Gesellsch. d. Wiss. zu Göttingen, Math-phys. Klasse, 235–257.

2. **Peskin, M. E., & Schroeder, D. V.** (1995). *An Introduction to Quantum Field Theory*. Addison-Wesley.

3. **Sakurai, J. J.** (1967). *Advanced Quantum Mechanics*. Addison-Wesley.

4. **Bjorken, J. D., & Drell, S. D.** (1964). *Relativistic Quantum Mechanics*. McGraw-Hill.

---


<!-- LATEX_PROTECTION_END -->

---
*Chapter 6 of "Noether Theorem Conversations" | Generated by Humanizer Lighthouse*
*Protected LaTeX content with fallback formatting*
