import React from 'react';
import { Box } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

interface PortalAnimationProps {
    show: boolean;
}

const PortalAnimation: React.FC<PortalAnimationProps> = ({ show }) => {
    return (
        <AnimatePresence>
            {show && (
                <Box
                    sx={{
                        position: 'fixed',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        zIndex: 9999,
                        pointerEvents: 'none',
                        width: '500px',
                        height: '500px',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center'
                    }}
                >
                    {/* Outer Glow */}
                    <motion.div
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1.2, opacity: 0.4 }}
                        exit={{ scale: 0, opacity: 0 }}
                        transition={{ duration: 0.5 }}
                        style={{
                            position: 'absolute',
                            width: '100%',
                            height: '100%',
                            borderRadius: '50%',
                            background: 'radial-gradient(circle, #39FF14 0%, rgba(57, 255, 20, 0) 70%)',
                            filter: 'blur(30px)'
                        }}
                    />

                    {/* Layer 1: Dark base swirl */}
                    <motion.div
                        initial={{ scale: 0, rotate: 0 }}
                        animate={{ 
                            scale: 1, 
                            rotate: 360,
                            borderRadius: ["40% 60% 70% 30% / 40% 50% 60% 50%", "60% 40% 30% 70% / 50% 60% 40% 60%", "40% 60% 70% 30% / 40% 50% 60% 50%"]
                        }}
                        exit={{ scale: 0 }}
                        transition={{ 
                            rotate: { duration: 3, repeat: Infinity, ease: "linear" },
                            borderRadius: { duration: 2, repeat: Infinity, ease: "easeInOut" },
                            scale: { duration: 0.5 }
                        }}
                        style={{
                            position: 'absolute',
                            width: '400px',
                            height: '400px',
                            background: 'conic-gradient(from 0deg, #166534, #14532d, #39FF14, #166534)',
                            boxShadow: '0 0 30px #166534',
                            opacity: 0.4
                        }}
                    />

                    {/* Layer 2: Main green swirl */}
                    <motion.div
                        initial={{ scale: 0, rotate: 0 }}
                        animate={{ 
                            scale: 0.9, 
                            rotate: -360,
                            borderRadius: ["50% 50% 50% 50% / 40% 40% 60% 60%", "40% 60% 40% 60% / 50% 50% 50% 50%", "50% 50% 50% 50% / 40% 40% 60% 60%"]
                        }}
                        exit={{ scale: 0 }}
                        transition={{ 
                            rotate: { duration: 2, repeat: Infinity, ease: "linear" },
                            borderRadius: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
                            scale: { duration: 0.5 }
                        }}
                        style={{
                            position: 'absolute',
                            width: '380px',
                            height: '380px',
                            background: 'conic-gradient(from 90deg, #39FF14, #90E900, #4ade80, #39FF14)',
                            opacity: 0.5
                        }}
                    />

                    {/* Layer 3: Inner bright blobs */}
                    <motion.div
                        initial={{ scale: 0, rotate: 0 }}
                        animate={{ 
                            scale: 0.7, 
                            rotate: 720,
                            borderRadius: ["30% 70% 70% 30% / 30% 30% 70% 70%", "70% 30% 30% 70% / 70% 70% 30% 30%", "30% 70% 70% 30% / 30% 30% 70% 70%"]
                        }}
                        exit={{ scale: 0 }}
                        transition={{ 
                            rotate: { duration: 1.5, repeat: Infinity, ease: "linear" },
                            borderRadius: { duration: 1, repeat: Infinity, ease: "easeInOut" },
                            scale: { duration: 0.5 }
                        }}
                        style={{
                            position: 'absolute',
                            width: '250px',
                            height: '250px',
                            background: 'radial-gradient(circle, #fff 0%, #39FF14 50%, transparent 100%)',
                            opacity: 0.6
                        }}
                    />
                </Box>
            )}
        </AnimatePresence>
    );
};

export default PortalAnimation;
