import { useContext, useEffect, useMemo, useState } from 'react'
import styles from './Draft.module.css'
import { useLocation, useNavigate } from 'react-router-dom'
import TitleCard from '../../components/DraftCards/TitleCard'
import SectionCard from '../../components/DraftCards/SectionCard'
import { Document, Packer, Paragraph, TextRun } from 'docx'
import { saveAs } from 'file-saver'
import { AppStateContext } from '../../state/AppProvider'
import { CommandBarButton, Stack } from '@fluentui/react';
import { Section } from '../../api/models'

const Draft = (): JSX.Element => {
  console.log('🎯 Draft component loading...');
  
  const appStateContext = useContext(AppStateContext)
  const location = useLocation()
  const navigate = useNavigate()

  console.log('🎯 Draft component state:', {
    appStateContext: !!appStateContext,
    location: location.pathname,
    hasState: !!appStateContext?.state
  });

  // get draftedDocument from context
  const draftedDocument = appStateContext?.state.draftedDocument
  const currentChat = appStateContext?.state.currentChat
  const draftedDocumentTitle = appStateContext?.state.draftedDocumentTitle;
  const sections = draftedDocument?.sections ?? []

  console.log('🎯 Draft data:', {
    draftedDocument: !!draftedDocument,
    sectionsCount: sections.length,
    draftedDocumentTitle,
    currentChatTitle: currentChat?.title
  });

  const isLoadedSections = appStateContext?.state.isLoadedSections

  const aiWarningLabel = 'AI-generated content may be incorrect'


  const [isExportButtonDisable, setIsExportButtonDisable] = useState<boolean>(false)

  useMemo(() => {
      if (currentChat?.title) {
        console.log(`🏷️ Setting document title from chat: "${currentChat.title}"`);
        appStateContext?.dispatch({ type: 'UPDATE_DRAFTED_DOCUMENT_TITLE', payload: currentChat.title })
      }
  }, [currentChat?.title])

  useEffect(() => {
    // Ensure there's always a default title if none exists
    if (!draftedDocumentTitle || draftedDocumentTitle.trim() === '') {
      console.log('📝 No title found, setting default title');
      appStateContext?.dispatch({ 
        type: 'UPDATE_DRAFTED_DOCUMENT_TITLE', 
        payload: currentChat?.title || 'Draft Document' 
      });
    }

    return () => {
      appStateContext?.dispatch({ type: 'UPDATE_IS_LOADED_SECTIONS', payload: { section: null, 'act': 'removeAll' } })
    }

  }, []);



  useEffect(() => {
    const title = draftedDocumentTitle ?? '' // Normalize null to ''
    
    // Debug information
    console.log('Export button condition check:', {
      isLoadedSectionsLength: isLoadedSections?.length || 0,
      sectionsLength: sections.length,
      titleLength: title.length,
      title: title,
      isLoadedSections: isLoadedSections,
      sections: sections
    });
    
    if (isLoadedSections?.length === sections.length && title.length > 0) {
      console.log('✅ Export button ENABLED - All conditions met');
      setIsExportButtonDisable(false);
    }
    else {
      console.log('❌ Export button DISABLED - Conditions not met:', {
        sectionsAllLoaded: isLoadedSections?.length === sections.length,
        titleExists: title.length > 0
      });
      setIsExportButtonDisable(true);
    }
  }, [isLoadedSections, draftedDocumentTitle])


  if (!draftedDocument) {
    console.log('❌ No draftedDocument found, showing instructions');
    // Instead of navigating away, show a message encouraging document generation
    return (
      <Stack className={styles.container}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <h2>No Document to Draft</h2>
          <p>To create a draft, please:</p>
          <ol style={{ textAlign: 'left', display: 'inline-block' }}>
            <li>Go to the <strong>Generate</strong> tab</li>
            <li>Ask AI to generate a document (e.g., "Generate a promissory note for $50,000")</li>
            <li>Click the <strong>Generate Draft</strong> button after AI responds</li>
            <li>Return here to edit and export your document</li>
          </ol>
          <button 
            onClick={() => navigate('/generate')} 
            style={{ 
              marginTop: '1rem', 
              padding: '10px 20px', 
              backgroundColor: '#1367CF', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Go to Generate Tab
          </button>
        </div>
      </Stack>
    )
  }

  console.log('✅ draftedDocument exists, proceeding with render');

  const cleanAllMarkdown = (text: string): string => {
    // Remove all markdown symbols
    return text
      .replace(/\*+/g, '')           // Remove all asterisks (*, **, ***, etc.)
      .replace(/#+\s*/g, '')         // Remove hash symbols for headings
      .replace(/`+/g, '')            // Remove backticks
      .replace(/~+/g, '')            // Remove tildes
      .replace(/_{2,}/g, '')         // Remove double underscores
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert links to plain text
      .replace(/^\s*[-+*]\s+/gm, '') // Remove bullet point markers
      .replace(/^\s*\d+\.\s+/gm, '')  // Remove numbered list markers (but we'll handle these separately)
      .replace(/\|/g, '')            // Remove table pipes
      .replace(/>/g, '')             // Remove blockquote markers
      .trim();
  }

  const parseMarkdownContent = (content: string): Paragraph[] => {
    const paragraphs: Paragraph[] = [];
    const lines = content.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      const originalLine = lines[i].trim();
      
      // Skip empty lines and separators
      if (!originalLine || originalLine === '---') {
        paragraphs.push(new Paragraph({
          children: [new TextRun({ text: '', size: 24, font: 'Times New Roman' })],
          spacing: { line: 240 }
        }));
        continue;
      }
      
      // Handle headings - clean the text first
      if (originalLine.startsWith('####')) {
        const cleanText = cleanAllMarkdown(originalLine.replace(/^####\s*/, ''));
        paragraphs.push(new Paragraph({
          children: [
            new TextRun({
              text: cleanText,
              bold: true,
              size: 28,
              font: 'Times New Roman'
            })
          ],
          spacing: { before: 240, after: 120, line: 240 }
        }));
      } else if (originalLine.startsWith('###')) {
        const cleanText = cleanAllMarkdown(originalLine.replace(/^###\s*/, ''));
        paragraphs.push(new Paragraph({
          children: [
            new TextRun({
              text: cleanText,
              bold: true,
              size: 32,
              font: 'Times New Roman'
            })
          ],
          spacing: { before: 240, after: 120, line: 240 }
        }));
      } else if (originalLine.startsWith('##')) {
        const cleanText = cleanAllMarkdown(originalLine.replace(/^##\s*/, ''));
        paragraphs.push(new Paragraph({
          children: [
            new TextRun({
              text: cleanText,
              bold: true,
              size: 36,
              font: 'Times New Roman'
            })
          ],
          spacing: { before: 240, after: 120, line: 240 }
        }));
      } else if (originalLine.startsWith('#')) {
        const cleanText = cleanAllMarkdown(originalLine.replace(/^#\s*/, ''));
        paragraphs.push(new Paragraph({
          children: [
            new TextRun({
              text: cleanText,
              bold: true,
              size: 40,
              font: 'Times New Roman'
            })
          ],
          spacing: { before: 240, after: 120, line: 240 }
        }));
      }
      // Handle bullet points
      else if (originalLine.startsWith('- ')) {
        const bulletText = cleanAllMarkdown(originalLine.replace(/^-\s*/, ''));
        if (bulletText) {
          paragraphs.push(new Paragraph({
            children: [
              new TextRun({ text: '• ', size: 24, font: 'Times New Roman' }),
              new TextRun({ text: bulletText, size: 24, font: 'Times New Roman' })
            ],
            spacing: { line: 240 },
            indent: { left: 720 }
          }));
        }
      }
      // Handle numbered lists
      else if (/^\d+\.\s/.test(originalLine)) {
        const listText = cleanAllMarkdown(originalLine.replace(/^\d+\.\s*/, ''));
        const match = originalLine.match(/^(\d+)\.\s*/);
        const number = match ? match[1] : '1';
        if (listText) {
          paragraphs.push(new Paragraph({
            children: [
              new TextRun({ text: `${number}. `, size: 24, font: 'Times New Roman' }),
              new TextRun({ text: listText, size: 24, font: 'Times New Roman' })
            ],
            spacing: { line: 240 },
            indent: { left: 720 }
          }));
        }
      }
      // Handle regular paragraphs
      else {
        const cleanText = cleanAllMarkdown(originalLine);
        if (cleanText) {
          paragraphs.push(new Paragraph({
            children: [new TextRun({ text: cleanText, size: 24, font: 'Times New Roman' })],
            spacing: { line: 240 }
          }));
        }
      }
    }
    
    return paragraphs;
  }

  const parseBoldText = (text: string): TextRun[] => {
    // Clean all markdown from the text
    const cleanText = cleanAllMarkdown(text);
    
    if (!cleanText.trim()) {
      return [];
    }
    
    // Return clean text without any markdown symbols
    return [new TextRun({ text: cleanText, size: 24, font: 'Times New Roman' })];
  }

  const exportToWord = () => {
    const doc = new Document({
      sections: [
        {
          properties: {
            page: {
              margin: {
                top: 1440,    // 1 inch
                right: 1440,  // 1 inch
                bottom: 1440, // 1 inch
                left: 1440    // 1 inch
              }
            }
          },
          children: [
            // Document title
            new Paragraph({
              children: [
                new TextRun({
                  text: getTitle(),
                  bold: true,
                  size: 48,
                  font: 'Times New Roman',
                  color: '1f4e79'
                })
              ],
              alignment: 'center',
              spacing: { after: 480, line: 240 }
            }),
            
            // AI warning
            new Paragraph({
              children: [
                new TextRun({
                  text: aiWarningLabel,
                  size: 20,
                  italics: true,
                  font: 'Times New Roman',
                  color: '666666'
                })
              ],
              alignment: 'center',
              spacing: { after: 480, line: 240 }
            }),
            
            // Process each section
            ...sections.flatMap((section, index) => {
              const sectionParagraphs: Paragraph[] = [];
              
              // Section title
              sectionParagraphs.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `${index + 1}. ${section.title}`,
                      bold: true,
                      size: 32,
                      font: 'Times New Roman',
                      color: '1f4e79'
                    })
                  ],
                  spacing: { before: 480, after: 240, line: 240 }
                })
              );
              
              // Section content
              if (section.content && section.content.trim()) {
                const contentParagraphs = parseMarkdownContent(section.content);
                sectionParagraphs.push(...contentParagraphs);
              }
              
              // Add spacing after section
              sectionParagraphs.push(
                new Paragraph({
                  children: [new TextRun({ text: '', size: 24, font: 'Times New Roman' })],
                  spacing: { after: 240, line: 240 }
                })
              );
              
              return sectionParagraphs;
            })
          ]
        }
      ]
    });

    Packer.toBlob(doc).then(blob => {
      saveAs(blob, `${sanitizeTitle(getTitle())}.docx`)
    })
  }

  function getTitle() {
    if (appStateContext === undefined) return ''
    return appStateContext.state.draftedDocumentTitle === null ? '' : appStateContext.state.draftedDocumentTitle
  }
  function sanitizeTitle(title: string): string {
    return title.replace(/[^a-zA-Z0-9]/g, '')
  }

  console.log('🎨 Rendering sections:', {
    sectionsLength: sections.length,
    sections
  });

  return (
    <Stack className={styles.container}>
      <TitleCard />
      {sections.map((section, index) => {
        console.log(`🔍 Rendering SectionCard ${index} for section:`, section);
        return <SectionCard key={index} sectionIdx={index} />
      })}
      <Stack className={styles.buttonContainer}>
        <CommandBarButton
          role="button"
          styles={{
            icon: {
              color: '#FFFFFF'
            },
            iconDisabled: {
              color: '#BDBDBD !important'
            },
            root: {
              color: '#FFFFFF',
              background: '#1367CF'
            },
            rootDisabled: {
              background: '#F0F0F0'
            }
          }}
          className={styles.exportDocumentIcon}
          iconProps={{ iconName: 'WordDocument' }}
          onClick={exportToWord}
          aria-label="export document"
          text="Export Document"
          disabled={isExportButtonDisable}
        />
      </Stack>
    </Stack>
  )
}

export default Draft
