import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageCircle, 
  Brain, 
  Send, 
  Loader2, 
  CheckCircle, 
  ArrowRight, 
  Lightbulb,
  Target,
  Sparkles
} from 'lucide-react'
import { cn } from '../utils'

const MaieuticDialogue = ({ narrative, onComplete, isActive }) => {
  const [sessionId, setSessionId] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [turns, setTurns] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isStarted, setIsStarted] = useState(false)
  const [insights, setInsights] = useState([])
  const [finalUnderstanding, setFinalUnderstanding] = useState('')
  const [suggestedConfig, setSuggestedConfig] = useState(null)
  const [goal, setGoal] = useState('understand')
  const [depthLevel, setDepthLevel] = useState(0)

  const startSession = async () => {
    if (!narrative.trim()) return
    
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:8100/maieutic/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ narrative, goal })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to start session: ${response.status}`)
      }
      
      const data = await response.json()
      setSessionId(data.session_id)
      setCurrentQuestion(data.first_question)
      setIsStarted(true)
    } catch (error) {
      console.error('Failed to start maieutic session:', error)
      alert(`Failed to start maieutic session: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (!answer.trim() || !sessionId) return
    
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:8100/maieutic/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question: currentQuestion,
          answer: answer,
          depth_level: depthLevel
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to submit answer: ${response.status}`)
      }
      
      const data = await response.json()
      
      // Add current turn to history
      setTurns(prev => [...prev, {
        question: currentQuestion,
        answer: answer,
        insights: data.insights,
        depth_level: depthLevel
      }])
      
      // Set up next question
      setCurrentQuestion(data.question)
      setAnswer('')
      setDepthLevel(prev => prev + 1)
      
      // Accumulate insights
      setInsights(prev => [...prev, ...data.insights])
      
    } catch (error) {
      console.error('Failed to submit answer:', error)
      alert(`Failed to submit answer: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const completeSession = async () => {
    if (!sessionId) return
    
    setIsLoading(true)
    try {
      const response = await fetch(`http://127.0.0.1:8100/maieutic/complete?session_id=${sessionId}`, {
        method: 'POST'
      })
      
      const data = await response.json()
      setFinalUnderstanding(data.final_understanding)
      setSuggestedConfig(data.suggested_config)
      
      // Call parent completion handler
      onComplete && onComplete({
        understanding: data.final_understanding,
        suggestedConfig: data.suggested_config,
        enrichedNarrative: data.enriched_narrative,
        insights: insights
      })
      
    } catch (error) {
      console.error('Failed to complete session:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateNewQuestion = async () => {
    if (!sessionId) return
    
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:8100/maieutic/question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          depth_level: depthLevel
        })
      })
      
      const data = await response.json()
      setCurrentQuestion(data.question)
      setAnswer('') // Clear current answer
    } catch (error) {
      console.error('Failed to generate new question:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (answer.trim()) {
        submitAnswer()
      }
    }
  }

  if (!isActive) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-semibold">Maieutic Dialogue</h2>
          <div className="flex items-center space-x-2 text-sm text-purple-300">
            <Target className="w-4 h-4" />
            <span>Goal: {goal}</span>
          </div>
        </div>
        
        <p className="text-muted-foreground mb-4">
          Through guided questions, we'll explore the deeper meaning of your narrative using the Socratic method.
        </p>
        
        {!isStarted && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Exploration Goal</label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400"
              >
                <option value="understand">Understand deeper meaning</option>
                <option value="clarify">Clarify assumptions</option>
                <option value="discover">Discover new perspectives</option>
                <option value="question">Question foundations</option>
              </select>
            </div>
            
            <button
              onClick={startSession}
              disabled={isLoading || !narrative.trim()}
              className={cn(
                "w-full px-4 py-2 rounded-lg font-medium transition-all",
                "bg-purple-600 hover:bg-purple-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center justify-center space-x-2"
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Starting dialogue...</span>
                </>
              ) : (
                <>
                  <MessageCircle className="w-4 h-4" />
                  <span>Begin Socratic Exploration</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Dialogue History */}
      <AnimatePresence>
        {turns.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {turns.map((turn, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass rounded-2xl p-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-medium">
                      Q
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm font-medium">Question</span>
                        <span className="text-xs text-purple-300 px-2 py-1 rounded-full bg-purple-600/20">
                          Depth {turn.depth_level}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{turn.question}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
                      A
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium mb-1">Your Response</div>
                      <p className="text-sm text-muted-foreground">{turn.answer}</p>
                    </div>
                  </div>
                  
                  {turn.insights.length > 0 && (
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 rounded-full bg-yellow-600 flex items-center justify-center text-white text-sm">
                        <Lightbulb className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium mb-2">Insights Discovered</div>
                        <ul className="space-y-1">
                          {turn.insights.map((insight, i) => (
                            <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                              <span className="text-yellow-400 mt-1">•</span>
                              <span>{insight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Current Question */}
      {isStarted && currentQuestion && !finalUnderstanding && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-sm font-medium">
                Q
              </div>
              <div className="flex items-center space-x-2">
                <span className="font-medium">Current Question</span>
                <span className="text-xs text-purple-300 px-2 py-1 rounded-full bg-purple-600/20">
                  Depth {depthLevel}
                </span>
              </div>
            </div>
            <button
              onClick={generateNewQuestion}
              disabled={isLoading}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium transition-all",
                "bg-blue-600 hover:bg-blue-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
              title="Generate a different question at the same depth"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <span>🎲</span>
                  <span>Try Another Question</span>
                </>
              )}
            </button>
          </div>
          
          <p className="text-lg mb-4">{currentQuestion}</p>
          
          <div className="space-y-3">
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Share your thoughts... (Press Enter to submit)"
              className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
              rows={3}
            />
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={submitAnswer}
                  disabled={isLoading || !answer.trim()}
                  className={cn(
                    "px-4 py-2 rounded-lg font-medium transition-all",
                    "bg-purple-600 hover:bg-purple-700 text-white",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    "flex items-center space-x-2"
                  )}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Submit Answer</span>
                    </>
                  )}
                </button>
                
                {turns.length >= 2 && (
                  <button
                    onClick={completeSession}
                    disabled={isLoading}
                    className={cn(
                      "px-4 py-2 rounded-lg font-medium transition-all",
                      "bg-green-600 hover:bg-green-700 text-white",
                      "disabled:opacity-50 disabled:cursor-not-allowed",
                      "flex items-center space-x-2"
                    )}
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Complete Dialogue</span>
                  </button>
                )}
              </div>
              
              <div className="text-sm text-muted-foreground">
                {turns.length} turn{turns.length !== 1 ? 's' : ''} completed
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Final Understanding */}
      {finalUnderstanding && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Sparkles className="w-6 h-6 text-yellow-400" />
            <h3 className="text-xl font-semibold">Emergent Understanding</h3>
          </div>
          
          <p className="text-lg mb-6">{finalUnderstanding}</p>
          
          {suggestedConfig && (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <ArrowRight className="w-4 h-4 text-purple-400" />
                <span className="font-medium">Suggested Projection Configuration</span>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 bg-white/5 rounded-lg">
                  <div className="text-sm text-muted-foreground">Persona</div>
                  <div className="font-medium">{suggestedConfig.persona}</div>
                </div>
                <div className="p-3 bg-white/5 rounded-lg">
                  <div className="text-sm text-muted-foreground">Namespace</div>
                  <div className="font-medium">{suggestedConfig.namespace}</div>
                </div>
                <div className="p-3 bg-white/5 rounded-lg">
                  <div className="text-sm text-muted-foreground">Style</div>
                  <div className="font-medium">{suggestedConfig.style}</div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

export default MaieuticDialogue