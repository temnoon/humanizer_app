import React from 'react'
import { motion } from 'framer-motion'

const LighthouseBeacon = () => {
  return (
    <div className="relative w-12 h-12">
      {/* Lighthouse base */}
      <svg
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
      >
        <path
          d="M12 2L13 7H19L14.5 10L16 15L12 12L8 15L9.5 10L5 7H11L12 2Z"
          fill="currentColor"
          className="text-purple-400"
        />
      </svg>
      
      {/* Animated beam */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "linear"
        }}
      >
        <div className="absolute top-1/2 left-1/2 w-px h-20 bg-gradient-to-t from-purple-400 to-transparent transform -translate-x-1/2 -translate-y-full origin-bottom lighthouse-beam" />
      </motion.div>
    </div>
  )
}

export default LighthouseBeacon
