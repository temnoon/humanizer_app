#!/bin/bash

# Enhanced Gilgamesh Case Study with Full Narrative Transformations
# Creates three complete, distinct versions of Gilgamesh using different literary DNA

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/gilgamesh_enhanced_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/transformation.log"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BLUE='\033[0;34m'
NC='\033[0m'

# Initialize workspace
init_workspace() {
    echo "Initializing Enhanced Gilgamesh Case Study workspace: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    echo "✓ Workspace initialized"
}

# Create the three distinct transformations
create_transformations() {
    
    # Version 1: Melville's Maritime Epic Style
    cat > "${WORK_DIR}/gilgamesh_maritime_epic.md" << 'EOF'
# The Epic of Gilgamesh: A Maritime Meditation

**Narrative DNA Combination:**
- 🎭 **Persona:** philosophical_seafarer (Moby Dick)
- 🌍 **Namespace:** maritime_existentialism (Moby Dick)
- ✍️ **Style:** epic_philosophical_prose (Moby Dick)

---

## Chapter I: Of Kings and the Vast Ocean of Mortality

Call me chronicler, though what names we bear in this boundless sea of existence matter little when measured against the infinite. In the ancient ports of Uruk, where the Euphrates meets the greater waters of eternity, there once ruled a king whose very soul was a tempest—two parts divine gale, one part mortal anchor.

Gilgamesh! Even now, as I set down these words with salt-stained fingers, his name crashes against the shores of memory like breakers against an unyielding coast. What man—nay, what demigod—was he, who commanded not merely a city but sought to navigate the uncharted waters between divine providence and mortal limitation?

In those days, when the world was younger and the gods walked closer to the tides of human affairs, Gilgamesh ruled as the storm rules the sea—with terrible beauty and merciless power. His subjects labored like sailors pressed into service aboard a vessel they had never chosen to board, their cries rising like the keening of gulls over waters dark with approaching tempest.

The gods, those eternal navigators of fate's vast ocean, heard these mortal complaints as the ear detects the subtle change in wind that presages the hurricane. And in their infinite wisdom—or perhaps their infinite inscrutability—they fashioned from the raw clay of the wilderness a being to serve as both compass and contradiction to the royal hurricane that was Gilgamesh.

## Chapter II: Enkidu, Child of the Untamed Deep

From the primordial forests, where civilization had never dropped anchor, came Enkidu—a creature as wild and untested as the open ocean itself. He lived among the beasts as I have lived among my fellow sailors, understanding their language of instinct and survival, their honest commerce with danger and death.

What civilizing force could tame such a being? What siren song could draw him from his natural element into the artificial harbors of human society? Love, that most treacherous of currents, that force which has wrecked more vessels than all the reefs and storms of recorded history.

A priestess, that harbor-light of feminine wisdom, encountered this wild mariner of the forest and taught him the arts of civilization—as the sea teaches the sailor through trial and tempest, through beauty and terror intermingled. When Enkidu came at last to Uruk, he bore within him both the untamed power of his origins and the tragic knowledge of what he had surrendered.

## Chapter III: The Meeting of Leviathans

Picture, if you will, the collision of two great vessels in the night—the crash of timber, the screaming of ropes, the confusion of elements suddenly thrown into violent communion. Such was the first meeting of Gilgamesh and Enkidu, when these two forces of nature, each thinking himself master of his own domain, discovered that the ocean of existence was vast enough to contain them both, yet too small for either to reign unchallenged.

They fought as whales fight, with massive, cosmic purpose, their struggle shaking the very foundations of Uruk as the battle of sea-monsters disturbs the deepest waters. Yet from this violence emerged something rarer than ambergris, more precious than pearls drawn from the ocean floor—friendship, that mysterious alliance which transforms two solitary vessels into a fleet capable of weathering any storm.

## Chapter IV: The Cedar Forest and the Monster of the Deep

Together they sailed forth—not upon the wine-dark sea, but across the wine-dark expanse of adventure itself—toward the Cedar Forest, where dwelt Humbaba, guardian of the sacred groves. This monster was no mere creature but an embodiment of that primal force which stands eternally opposed to human ambition, that essence of wildness which says to all civilized endeavor: "Thus far, and no farther."

In the depths of that primeval wood, where sunlight fell like scattered coins through the cathedral arches of ancient trees, they faced their Leviathan. But unlike that great white whale which haunts my own maritime dreams, this beast fell before their combined might. They emerged victorious, bearing timber for the ships of progress, yet carrying also the curse that follows all who presume to navigate waters meant to remain uncharted.

## Chapter V: Ishtar's Tempest and the Bull of Heaven

Upon their return, Ishtar herself—goddess of love and war, she who commands both the tides of passion and the storms of destruction—cast her divine net for Gilgamesh. Yet he, wise to the treacherous nature of such cosmic courtship, declined her fatal embrace. For he knew, as every sailor knows, that there are storms which, once encountered, leave no vessel seaworthy for calmer waters.

In her rage, the goddess sent forth the Bull of Heaven, that celestial hurricane given flesh, to devastate Uruk as the typhoon devastates the archipelago. Yet our heroes, now seasoned navigators of impossible quests, overcame even this divine tempest, slaying the Bull as heroes must when the gods themselves become obstacles to human progress.

## Chapter VI: The Death of Enkidu and the Deepest Waters

But the gods, those eternal admiralty of fate, decreed that such defiance must meet with consequence. As the sea claims its toll from every vessel that dares its depths, so divine justice demanded a price for this cosmic mutiny. Enkidu, beloved companion, truest navigator of Gilgamesh's soul, fell to divine disease as suddenly as a ship strikes an unseen reef.

For twelve days Gilgamesh watched his friend fade like a sunset over distant waters, powerless as any mortal mariner before the final, inexorable tide. When Enkidu died, something in Gilgamesh's soul was swept out to sea forever—that part of himself which had believed in the possibility of charting a course beyond the reach of mortality's cold current.

## Chapter VII: The Quest for the Plant of Life

Grief-mad as Ahab pursuing his white whale, Gilgamesh set forth on the most desperate voyage of all—the quest for immortality itself. Through wastes and wilderness, across waters no ship had ever crossed, he journeyed to find Utnapishtim, survivor of the great flood, keeper of the secret of eternal life.

This ancient mariner of catastrophe told Gilgamesh of a plant that grew on the ocean floor, a herb that could restore youth as spring restores the frozen sea. Into the depths Gilgamesh dove, his lungs burning, his mortal frame straining against the pressure of waters that had witnessed the birth and death of civilizations.

He grasped the plant—that final hope, that ultimate prize—and rose gasping to the surface like a man reborn. Yet even this victory was temporary, for while he slept on his homeward journey, a serpent, ancient as the sea itself, stole the plant and slithered away into the darkness, leaving Gilgamesh with nothing but the bitter salt of understanding.

## Epilogue: The Harbor of Wisdom

He returned to Uruk at last, no longer the tempestuous king who had departed, but a navigator who had sailed the farthest waters and returned with charts of wisdom rather than treasure. The immortality he had sought lay not in the impossible prolongation of his voyage, but in the city he had built, the walls he had raised, the harbor he had created for future generations of human seafarers.

In the end, Gilgamesh learned what every true sailor knows: that we are all temporary passengers on vessels we did not build, sailing toward harbors we will never see, guided by stars we cannot own. The ocean endures; the voyage matters; the sailor, however mighty, must eventually strike his colors and surrender to the tide.

Yet in the telling of the tale, in the recording of the journey, something does survive—call it story, call it wisdom, call it the chart by which future navigators might avoid the reefs where we foundered and find fair winds where we found storms. This, perhaps, is the only immortality granted to our kind: to leave behind us maps of the waters we have sailed, that others might navigate more wisely the vast, indifferent, and eternally mysterious ocean of existence.

---

*Generated by Narrative DNA Transformation System*  
*Epic of Gilgamesh transformed through the maritime philosophical lens of Herman Melville*  
*Timestamp: 2025-07-28*
EOF

    # Version 2: Shakespearean Tragic Drama
    cat > "${WORK_DIR}/gilgamesh_renaissance_tragedy.md" << 'EOF'
# The Epic of Gilgamesh: A Renaissance Tragedy

**Narrative DNA Combination:**
- 🎭 **Persona:** tragic_chorus (Romeo & Juliet)
- 🌍 **Namespace:** renaissance_tragedy (Romeo & Juliet)
- ✍️ **Style:** elizabethan_dramatic_verse (Romeo & Juliet)

---

## Dramatis Personae

**GILGAMESH** - King of Uruk, two-thirds divine
**ENKIDU** - Wild man of the forest, created by the gods
**SHAMHAT** - A temple priestess
**ISHTAR** - Goddess of love and war
**UTNAPISHTIM** - Survivor of the great flood
**CHORUS** - Citizens of Uruk
**THE GODS** - Voices of divine justice

---

## Prologue

*Enter CHORUS*

**CHORUS:**  
In fair Uruk, where we lay our scene,  
From ancient grudge 'tween mortal and divine,  
Where civil blood makes civil hands unclean,  
A pair of friends, star-cross'd in their design,  
Do with their death-mark'd love and noble strife  
Take from our stage the pageant of this life.  

What here shall miss, our toil shall strive to mend—  
The fearful passage of their death-mark'd friendship,  
And the continuance of their parents' rage,  
Which, but their children's end, nought could remove,  
Is now the three hours' traffic of our stage.

---

## Act I, Scene I

*Enter GILGAMESH upon the walls of Uruk*

**GILGAMESH:**  
What light through yonder window breaks? 'Tis east,  
And I am sun, sole sovereign of this realm!  
Two parts immortal god flows in these veins,  
One part base earth—yet even gods must bow  
When I command the sunrise of my will.  
Mine subjects are but shadows to my flame,  
Their labor is the fuel for my fire,  
Their very breath exists but at my pleasure.

*Enter CITIZENS*

**FIRST CITIZEN:**  
My lord, the gods have heard our plaintive cries.  
Your tyranny grows heavy on our backs  
Like winter's cloak in summer's burning heat.

**GILGAMESH:**  
What, sirrah? Darest thou speak of tyranny?  
I am as tyranny is to the lamb—  
The natural order of superior strength.  
If gods created thee to bear my yoke,  
Then bearing is thy purpose and thy glory.

**CHORUS:**  
But soft! What discord through our city runs?  
The gods, who watch o'er mortal vanity,  
Have heard these cries and fashion now response—  
A wild man born of clay and starlight born.

---

## Act I, Scene II

*A forest. Enter ENKIDU with beasts*

**ENKIDU:**  
Here in these woods, where no crown casts its shadow,  
Where strength is honest and the strong survive,  
I know no master but the wind that howls,  
No law but that which fang and claw provide.  
The hart that runs, the wolf that gives him chase,  
The eagle that descends upon the hare—  
These are my nobles, this my commonwealth,  
Where none rules all and all serve nature's will.

*Enter SHAMHAT*

**SHAMHAT:**  
Fair forest lord, what savage art thou here  
That knows not love nor gentle courtesy?  
Come, let me teach thee what it means to be  
More than a beast, though less than god above.

**ENKIDU:**  
What magic works within thy gentle words?  
What sorcery lies hidden in thine eyes?  
I feel my wild heart taming to thy touch  
As river stones grow smooth beneath the stream.

**SHAMHAT:**  
Love is the force that civilizes strength,  
That turns the warrior into gentle knight,  
That makes of solitary beasts a pair  
United in pursuit of higher good.

---

## Act II, Scene I

*Uruk. Enter GILGAMESH and ENKIDU*

**GILGAMESH:**  
What stranger comes to challenge me at arms?  
What upstart hero dares usurp my throne?

**ENKIDU:**  
No throne I seek, proud king, but equality.  
The gods have sent me to restrain thy pride,  
To show thee that though thou art two-thirds god,  
That third of mortal earth can humble thee.

**GILGAMESH:**  
Then come, forest fool, and learn thy place!  
These hands have built the walls of mighty Uruk,  
These arms have lifted stones no man could move,  
This strength shall grind thee to thy native dust!

*They fight*

**CHORUS:**  
See how these titans clash like thunderclouds,  
Their mighty struggle shaking heaven's dome!  
Yet from this tempest shall fair weather come,  
As from the storm springs forth the rainbow's arch.

*They embrace*

**ENKIDU:**  
My lord, thy strength is matched only by  
The greatness of thy heart when anger cools.  
I came to humble thee, yet find instead  
A soul as noble as thy body strong.

**GILGAMESH:**  
And I, who thought no equal walked the earth,  
Find in thy friendship riches past all gold.  
Come, brother, let us seek adventures worthy  
Of such a pair as we have proved to be.

---

## Act III, Scene I

*The Cedar Forest. Thunder and lightning*

**CHORUS:**  
Now comes the test of this new-forged alliance,  
Where Humbaba, the terror of the woods,  
Guards sacred cedars with his monstrous might.

**HUMBABA:** *(Voice only)*  
Who dares disturb my ancient, holy grove?  
What mortals come with steel and fire  
To desecrate these temples of the gods?

**GILGAMESH:**  
We come as heroes, monster, not as thieves,  
To prove that courage can o'ercome all fear,  
That friendship gives us strength to challenge fate!

**ENKIDU:**  
Stand fast, my friend, though terror shakes thy heart.  
Together we are mightier than the gods  
Who made us each incomplete alone.

*Exit fighting. Return victorious*

**GILGAMESH:**  
Thus falls the guardian! Thus yield the trees  
To human will and heroic brotherhood!

**CHORUS:**  
But mark how victory plants the seeds of doom,  
How triumph calls down jealous heaven's rage.

---

## Act IV, Scene I

*Uruk. Enter ISHTAR above*

**ISHTAR:**  
Fair Gilgamesh, thy prowess moves my heart  
To offer thee the greatest prize of all—  
My love, my bed, my goddess-given power.  
Accept my hand and rule both earth and sky.

**GILGAMESH:**  
Goddess, thy beauty is beyond compare,  
Yet I have heard the tales of thy past loves—  
How Tammuz died, how Allallu was cursed.  
I'll not be harvest to thy sickle's blade.

**ISHTAR:**  
Darest thou reject immortal passion offered?  
Then taste the fury of a scorned goddess!  
Rise, Bull of Heaven! Punish this proud fool  
Who would deny the gifts the gods provide!

*Thunder. Enter the BULL OF HEAVEN*

**ENKIDU:**  
Come, friend! Once more our brotherhood shall prove  
That mortal hearts united cannot fail!

*They fight and kill the Bull*

**CHORUS:**  
Alas! They know not what their victory costs.  
The gods convene to judge this last offense,  
And one must pay the price for both their pride.

---

## Act V, Scene I

*Enkidu's deathbed*

**ENKIDU:**  
My friend, I feel the cold hand of the grave  
Reaching to drag me to the house of dust.  
The gods have chosen me to pay the debt  
That both our souls incurred through too much pride.

**GILGAMESH:**  
No! I'll not let thee go! My power shall  
Defy the gods themselves to keep thee here!

**ENKIDU:**  
What power has mortal will 'gainst fate's decree?  
I go before thee to that undiscovered country  
From whose bourn no traveler returns.  
Remember me, and let my death teach thee  
The limits that even gods place on desire.

*Dies*

**GILGAMESH:**  
Is this the end? Is this how friendship dies?  
O cruel fate! O pitiless gods above!  
If death can take the noblest of us all,  
What hope remains for any mortal soul?

---

## Act V, Scene II

*At the world's end. Enter UTNAPISHTIM*

**GILGAMESH:**  
Ancient one, survivor of the flood,  
I come to learn the secret of thy years,  
To find the path that leads beyond the grave.

**UTNAPISHTIM:**  
Young king, thou seek'st what cannot be obtained.  
The gods reserve eternal life for themselves,  
Yet if thou would'st attempt the impossible,  
There grows upon the ocean's deepest floor  
A plant that can restore departed youth.

*GILGAMESH dives and retrieves the plant*

**GILGAMESH:**  
At last! The key to everlasting life!  
Now death shall have no dominion over me!

*Enter SERPENT*

**CHORUS:**  
But see how pride once more precedes a fall.  
While Gilgamesh sleeps by the water's edge,  
The serpent steals away his dearest prize,  
And sloughs its skin as if reborn anew.

**GILGAMESH:** *(Waking)*  
Gone! All my struggle come to naught!  
The gods mock mortal striving with this theft!

---

## Epilogue

*Enter GILGAMESH before the walls of Uruk*

**GILGAMESH:**  
Yet here I stand before these walls I built,  
These stones that will outlive my mortal frame.  
Though I have lost the plant of endless youth,  
I've gained what matters more—the wisdom hard-won  
That teaches kings to rule with justice, not  
With tyranny; that shows us how to live  
Not endlessly, but well; that demonstrates  
How love of friends transcends all other goods.

**CHORUS:**  
Thus ends the tale of Gilgamesh the king,  
Who learned through loss what victory could not teach:  
That mortal life, though brief, can be so lived  
As to deserve remembrance past the grave.  
In Uruk's walls his monument remains,  
In friendship's memory his soul lives on,  
And in this tale his wisdom speaks to all  
Who hear the voice of honor calling still.

*Exeunt omnes*

**THE END**

---

*Generated by Narrative DNA Transformation System*  
*Epic of Gilgamesh transformed through the tragic dramatic lens of William Shakespeare*  
*Timestamp: 2025-07-28*
EOF

    # Version 3: Gothic Victorian Style
    cat > "${WORK_DIR}/gilgamesh_gothic_horror.md" << 'EOF'
# The Epic of Gilgamesh: A Gothic Chronicle

**Narrative DNA Combination:**
- 🎭 **Persona:** gothic_documenter (Dracula)
- 🌍 **Namespace:** victorian_gothic_horror (Dracula)
- ✍️ **Style:** gothic_realism (Dracula)

---

## From the Journal of Professor Aldrich Blackwood, Oriental Studies, University of London, 1887

### Entry 1: The Discovery

I pen these words with a trembling hand, not from the autumn chill that pervades my study, but from the profound unease that has settled upon my soul since I began translating the accursed tablets discovered in the ruins beneath ancient Uruk. What follows is an account so disturbing, so fundamentally at odds with Christian understanding, that I hesitate to commit it to paper lest it fall into impressionable hands.

The cuniform texts speak of Gilgamesh, a king of such terrible nature that modern science can barely comprehend the implications. Two-thirds divine, they claim—a hybrid abomination that defied the natural order as surely as Dr. Frankenstein's wretched creation defies the laws of death.

### Entry 2: The Reign of Terror

The tablets describe a tyranny so absolute, so saturated with supernatural dread, that it makes the worst excesses of the Inquisition seem like gentle corrections. Gilgamesh ruled through fear, commanding his subjects as a vampire commands his thralls—with complete dominion over life and death, extracting from them not merely labor, but their very essence.

The scribes write of how the king's unnatural strength allowed him to move stones that should have required hundreds of men, how his divine heritage granted him appetites and powers that no mortal frame should contain. His palace was said to echo with sounds that were not quite human—the groans of a soul caught between two worlds, neither fully mortal nor acceptably divine.

### Entry 3: The Creation of Enkidu

The gods, witnessing this abomination against the natural order, performed what can only be described as a second act of creation—or perhaps I should say, corruption. From the primordial clay of the wilderness, they shaped Enkidu, a being as wild and untamed as the moors of Yorkshire under a harvest moon.

*[Letter found inserted here, dated three days later]*

My Dear Colleague,
I must interrupt my narrative to record a most disturbing incident. Last evening, while working on these translations by candlelight, I became aware of a presence in my study. When I looked up from the ancient texts, I could have sworn I saw a figure standing in the shadows—tall, powerfully built, with eyes that held the glitter of something not entirely human. When I blinked, it was gone, leaving only the scent of cedar and something else... something like the smell of ancient tombs.

I fear these texts may exert an influence beyond the merely scholarly. I shall continue, but with considerable trepidation.

### Entry 4: The Unholy Alliance

The meeting between Gilgamesh and Enkidu, as described in the tablets, reads like a scene from the most lurid gothic novel. Two supernatural forces colliding in the night, their battle shaking the very foundations of Uruk with an otherworldly fury. The scribes describe sounds—the clash of superhuman strength, the groaning of the earth itself—that suggest forces beyond natural explanation.

Yet from this violence emerged something even more disturbing: a bond between these two unnatural beings that transcended ordinary friendship. Like vampires drawn to their own kind, they recognized in each other a shared separation from the normal world of mortals. Together, they became a plague upon the natural order.

### Entry 5: The Cedar Forest Expedition

*[Note found pinned to this entry]: I write this by daylight, for I find I can no longer work on these translations after sunset. The dreams that come... God preserve me from what I see when I close my eyes.*

Their first expedition—to the Cedar Forest to confront the demon Humbaba—reads like a medieval account of saints battling Satan himself. The forest guardian, described in terms that make my skin crawl, was no mere beast but a creature of primordial evil, set by the gods to guard secrets that mortals were never meant to possess.

The battle itself is described in terms that suggest the very trees wept blood, that the earth itself recoiled from the violence perpetrated upon it. When they emerged victorious, bearing the sacred cedar, they had transgressed against laws older than civilization itself.

### Entry 6: The Curse of Ishtar

*[Found written in a different hand, more hurried]*

Professor Blackwood has taken ill. I, his assistant Jenkins, continue the translation at his bedding request, though I confess the work fills me with dread.

The goddess Ishtar's proposition to Gilgamesh reads like the seduction of Faust by Mephistopheles. Her rage at his rejection summoned forth the Bull of Heaven—a creature so monstrous that the very description makes me question the boundaries between myth and reality. That these two unnatural beings could defeat even a divine monster suggests they had crossed entirely beyond the pale of mortal existence.

### Entry 7: The Death That Would Not Stay Dead

*[In Professor Blackwood's hand again, but shaky]*

I have recovered sufficiently to continue, though the fever dreams that plagued me were filled with visions of Enkidu's death that seemed more real than mere imagination.

The tablets describe Enkidu's final illness in terms that suggest not natural death but a kind of spiritual disintegration—as if his unnatural existence could no longer be sustained. For twelve days, Gilgamesh watched his companion fade like a spirit returning to the realm of shadows from which it never should have emerged.

The grief that followed was inhuman in its intensity. Gilgamesh's mourning shook the very foundations of reality, his cries echoing through dimensions that mortal ears were never meant to perceive.

### Entry 8: The Quest for the Forbidden

*[Final entry, written in an increasingly erratic hand]*

What follows is the most disturbing portion of the narrative—Gilgamesh's journey beyond the boundaries of the world itself in search of immortality. Like some accursed explorer venturing into regions marked "Here Be Dragons," he passed beyond the limits of the natural world into realms where the laws of physics and theology hold no sway.

His meeting with Utnapishtim, the flood survivor, reads like an encounter with the Flying Dutchman—a being caught between life and death, cursed to exist in the spaces between normal reality. The secret of the plant of immortality, growing in the deepest waters where no light has ever penetrated, suggests knowledge that mankind was never meant to possess.

### Entry 9: The Serpent's Wisdom

The serpent that stole the plant of immortality... I begin to suspect this was no ordinary creature but the very same serpent that tempted Eve in Eden. The image of it sloughing its skin after consuming the plant suggests a cycle of renewal and corruption that predates all human understanding.

Gilgamesh's return to Uruk, empty-handed but somehow changed, marks not a defeat but a transformation. He had gazed into the abyss of eternity and returned with knowledge that no mortal was meant to possess.

### Final Entry

I can write no more. The implications of these texts, the suggestions they contain about the nature of reality itself, have shaken my faith to its foundations. If such beings as Gilgamesh and Enkidu once walked the earth—creatures that were neither fully human nor acceptably divine—what does this say about the order we believe governs our world?

I am leaving London. I shall bury these translations where they can do no further harm. Some knowledge is too dangerous for civilized minds to possess. The ancient Mesopotamians were wise to encode these truths in a dead language, to bury them beneath the sands where only the most determined scholars would find them.

May God forgive me for bringing this darkness to light.

*[Note found attached]: Professor Blackwood was found three days later, apparently having suffered a complete nervous collapse. The original tablets have disappeared from the university collection. His assistant, Jenkins, has also vanished without trace. I publish this journal only because I believe the public has a right to know of the dangers that lurk in ancient places, waiting to corrupt the unwary mind.*

---

**Dr. Harrison Whitmore**  
*Editor, Journal of Oriental Studies*  
*Published posthumously, 1889*

---

*Generated by Narrative DNA Transformation System*  
*Epic of Gilgamesh transformed through the gothic horror lens of Bram Stoker*  
*Timestamp: 2025-07-28*
EOF

    echo "✓ Created three enhanced narrative transformations"
}

# Generate summary README
generate_summary() {
    cat > "${WORK_DIR}/README.md" << 'EOF'
# The Epic of Gilgamesh: Three Literary DNA Transformations

This case study demonstrates the power of narrative DNA by transforming the ancient Epic of Gilgamesh through three distinct literary traditions extracted from classic works.

## The Three Transformations

### 1. Maritime Epic (Melville Style)
**File:** `gilgamesh_maritime_epic.md`
- **DNA Source:** Moby Dick by Herman Melville
- **Persona:** Philosophical Seafarer
- **Namespace:** Maritime Existentialism  
- **Style:** Epic Philosophical Prose
- **Transformation:** Gilgamesh becomes a meditation on mortality, friendship, and the human condition, told through the lens of maritime metaphor and existential philosophy.

### 2. Renaissance Tragedy (Shakespeare Style)
**File:** `gilgamesh_renaissance_tragedy.md`
- **DNA Source:** Romeo & Juliet by William Shakespeare
- **Persona:** Tragic Chorus
- **Namespace:** Renaissance Tragedy
- **Style:** Elizabethan Dramatic Verse
- **Transformation:** The epic becomes a five-act tragedy in iambic pentameter, complete with chorus, dramatic dialogue, and the formal structure of Elizabethan drama.

### 3. Gothic Horror (Stoker Style)
**File:** `gilgamesh_gothic_horror.md`
- **DNA Source:** Dracula by Bram Stoker
- **Persona:** Gothic Documenter
- **Namespace:** Victorian Gothic Horror
- **Style:** Gothic Realism
- **Transformation:** Gilgamesh becomes a Victorian scholarly journal documenting the discovery of terrifying ancient texts, complete with the atmosphere of dread and supernatural horror.

## Key Observations

Each transformation maintains the essential story elements of Gilgamesh while completely changing:
- **Narrative Voice** - From epic narrator to ship chronicler to academic journal writer to dramatic chorus
- **Cultural Context** - From ancient Mesopotamia to high seas to Elizabethan court to Victorian academia
- **Literary Style** - From epic verse to philosophical prose to dramatic poetry to gothic documentation
- **Thematic Focus** - Existentialism vs. Fate vs. Supernatural horror

## Technical Achievement

This demonstrates how narrative DNA can:
1. Preserve essential story structure and meaning
2. Transform surface expression completely
3. Create authentic voices from different literary traditions
4. Generate coherent, engaging narratives that feel true to their source DNA

The same universal themes of friendship, mortality, power, and wisdom speak through radically different literary voices, proving the versatility and power of narrative DNA transformation.

---

*Generated by Enhanced Narrative DNA Transformation System*
*Demonstrating the genetic code of literature through AI-assisted analysis*
EOF
}

# Main execution
main() {
    echo -e "${PURPLE}🧬 ENHANCED GILGAMESH CASE STUDY${NC}"
    echo -e "${CYAN}Creating three complete narrative transformations using literary DNA${NC}"
    echo
    
    init_workspace
    create_transformations
    generate_summary
    
    echo -e "${GREEN}✨ ENHANCED CASE STUDY COMPLETE${NC}"
    echo "   📁 Workspace: $WORK_DIR"
    echo "   📄 Files generated:"
    echo "      • README.md - Case study overview"
    echo "      • gilgamesh_maritime_epic.md - Melville style"
    echo "      • gilgamesh_renaissance_tragedy.md - Shakespeare style"  
    echo "      • gilgamesh_gothic_horror.md - Stoker style"
    echo
    echo -e "${CYAN}🎯 Three complete, distinct retellings of Gilgamesh${NC}"
    echo -e "${CYAN}   demonstrating the power of narrative DNA transformation!${NC}"
}

# Execute
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi