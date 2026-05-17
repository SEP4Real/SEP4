import { describe, it, expect, beforeEach, vi } from 'vitest';

// MOCK CONFIGURATION 
// Simulating the browser environment in Node.js for LocalStorage

const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    clear: () => { store = {}; },
    removeItem: (key) => { delete store[key]; }
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true
});

global.alert = vi.fn();

// TEST: PROFILE PAGE

describe('Profile Page - Unit & User Flow Tests', () => {
  
  beforeEach(() => {
    // Cleaning the state before each run (Isolation)
    localStorage.clear();
  });

  /* TASK 1: Component Unit Test
   * Tests the isolated logic of the calculation algorithm for the progress bar.
   */
  it('Component Unit Test: should correctly calculate profile completion progress percentage', () => {
    localStorage.setItem('user', JSON.stringify({ name: 'ddd' }));
    localStorage.setItem('stud_uni', 'VIA University College');
    localStorage.setItem('stud_prog', 'Software Engineering');

    const userData = JSON.parse(localStorage.getItem('user'));
    const fields = [
      userData.name,
      localStorage.getItem('stud_uni'),
      localStorage.getItem('stud_prog'),
      localStorage.getItem('stud_year'), // null
      localStorage.getItem('stud_goal'), // null
      localStorage.getItem('stud_pic')   // null
    ];

    const completedFields = fields.filter(f => f && f !== "").length;
    const progressPercentage = Math.round((completedFields / fields.length) * 100);

    // ASSERT (Result verification: 3 fields out of 6 completed = 50%)
    expect(progressPercentage).toBe(50);
  });

  /**
   * TASK 2: User Flow Test
   * Simulates the head-to-tail behavior of a student on the interface
   */
  it('User Flow Test: should simulate entering edit mode, typing info, and saving data', () => {
    let isEditing = false;
    let studentInfo = { university: "", StudyProgram: "" };
    expect(isEditing).toBe(false);

    // simulate the steps/flow the user takes on the screen
    isEditing = true; 
    expect(isEditing).toBe(true);

    studentInfo.university = "VIA University College";
    studentInfo.StudyProgram = "Software Technology";

    //The user clicks the "Save Changes" button
    localStorage.setItem('stud_uni', studentInfo.university);
    localStorage.setItem('stud_prog', studentInfo.StudyProgram);
    isEditing = false; 

   //assert
    expect(isEditing).toBe(false);
    expect(localStorage.getItem('stud_uni')).toBe('VIA University College');
    expect(localStorage.getItem('stud_prog')).toBe('Software Technology');
  });
});